from iff.parser import Time, Record, File
from iff.model import Stop, Service, ServiceList
from iff.delivery import IdentificationRecord

from copy import copy

# Service record class
class ServiceRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      id = int(string[1:9]),
      service_numbers = [],
      attributes = [],
      stops = []
    )

# Service number record class
class ServiceNumberRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      company = context.companies.get(int(string[1:4])),
      service_number = int(string[5:10]),
      variant = string[11:18].strip(),
      first_stop = int(string[18:21]),
      last_stop = int(string[22:25]),
      service_name = string[26:56].strip()
    )

# Footnote record class
class FootnoteRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      footnote = context.footnotes.get(int(string[1:6])),
      first_stop = int(string[7:10]),
      last_stop = int(string[11:14])
    )

# Transport mode record class
class TransportModeRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      transport_mode = context.transport_modes.get(string[1:5].strip()),
      first_stop = int(string[6:9]),
      last_stop = int(string[10:13])
    )

# Attribute record class
class AttributeRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      attribute = context.attributes.get(string[1:5].strip()),
      first_stop = int(string[6:9]),
      last_stop = int(string[10:13])
    )

# First stop record class
class StartRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip()),
      departure_time = Time.parse(string[9:13])
    )

# Stop with direct continuation record class
class ContinuationRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip()),
      time = Time.parse(string[9:13])
    )

# No stop record class
class PassingRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip())
    )

# Stop with pause record class
class IntervalRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip()),
      arrival_time = Time.parse(string[9:13]),
      departure_time = Time.parse(string[14:18])
    )

# Last stop record class
class FinalRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip()),
      arrival_time = Time.parse(string[9:13])
    )

# Platform record class
class PlatformRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      arrival_platform_name = string[1:6].strip(),
      departure_platform_name = string[7:12].strip(),
      footnote = context.footnotes.get(int(string[13:18]))
    )


# Record identifiers
identifiers = {
  '#': ServiceRecord,
  '%': ServiceNumberRecord,
  '-': FootnoteRecord,
  '&': TransportModeRecord,
  '*': AttributeRecord,
  '>': StartRecord,
  '.': ContinuationRecord,
  ';': PassingRecord,
  '+': IntervalRecord,
  '<': FinalRecord,
  '?': PlatformRecord
}


# Service file
class ServiceFile(File, ServiceList):
  # Constructor
  def __init__(self, identification_record):
    File.__init__(self,identification_record)

  # Split a service in multiple services
  def _split_services(self, service_record):
    # For each service add a service to the file
    for service_number_record in service_record.service_numbers:
      # Create the stop list
      stop_idx = 0
      stops = []

      # Iterate over the stops and append them to the list
      for stop in service_record.stops:
        # Check if the service stops here
        if not stop.is_passing():
          stop_idx += 1

        # Add the stop if in the boundaries
        if stop_idx >= service_number_record.first_stop and stop_idx <= service_number_record.last_stop:
          stops.append(copy(stop))

      # Strip the stops
      stops[0].arrival_time = None
      stops[0].arrival_platform = ''
      stops[-1].departure_time = None
      stops[-1].departure_platform = ''

      # Create a new service
      service = Service(
        id = service_number_record.service_number,
        company = service_number_record.company,
        variant = service_number_record.variant,
        name = service_number_record.service_name,
        footnote = service_record.footnote,
        transport_mode = service_record.transport_mode,
        attributes = service_record.attributes,
        stops = stops
      )

      # Append the service
      self.append(service)

  # Read a file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new file
      identification_record = IdentificationRecord.read(next(file),context)
      timetable_file = cls(identification_record)

      # Initialize local variables
      current_service = None
      current_stop = None

      # Iterate over the file
      for string in file:
        # Get the record belonging to the identifier and parse it
        identifier = string[0]
        if identifier not in identifiers:
          raise RuntimeError('Invalid record type: {}'.format(identifier))

        record = identifiers.get(identifier).read(string,context)

        # Switch the record
        if isinstance(record,ServiceRecord):
          # Check if a service is selected, then add it
          if current_service is not None:
            timetable_file._split_services(current_service)

          # Create a new service
          current_service = record
          current_stop = None

        elif isinstance(record,ServiceNumberRecord):
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the service number
          current_service.service_numbers.append(record)

        elif isinstance(record,FootnoteRecord):
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the footnote
          current_service.footnote = record.footnote

        elif isinstance(record,TransportModeRecord):
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the transport mode
          current_service.transport_mode = record.transport_mode

        elif isinstance(record,AttributeRecord):
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the attribute
          current_service.attributes.append(record.attribute)

        elif type(record) in [StartRecord, ContinuationRecord, PassingRecord, IntervalRecord, FinalRecord]:
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the stop
          current_stop = Stop(**record.__dict__)
          current_service.stops.append(current_stop)

        elif isinstance(record,PlatformRecord):
          # Check if a stop is selected
          if current_stop is None:
            raise RuntimeError("No stop is selected")

          # Set the platforms
          current_stop.arrival_platform = record.arrival_platform_name
          current_stop.departure_platform = record.departure_platform_name

      # Add the last service
      if current_service is not None:
        timetable_file._split_services(current_service)

      # Return the file
      return timetable_file
