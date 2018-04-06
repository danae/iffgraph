from iff import Record, File, parse_time
from iff.delivery import IdentificationRecord

from copy import copy

# Stop class
class Stop:
  # Constructor
  def __init__(self, **kwargs):
    self.station = kwargs.get('station')
    self.arrival_time = kwargs.get('time') or kwargs.get('arrival_time')
    self.arrival_platform = (kwargs.get('arrival_platform') or '') if self.arrival_time else ''
    self.departure_time = kwargs.get('time') or kwargs.get('departure_time')
    self.departure_platform = (kwargs.get('departure_platform') or '') if self.departure_time else ''

  # Convert to string
  def __str__(self):
    return "{:<12}  {:<12}  {}".format(
      "A {:<5} {:<4}".format(self.arrival_time,self.arrival_platform) if self.arrival_time else '',
      "D {:<5} {:<4}".format(self.departure_time,self.departure_platform) if self.departure_time else '',
      self.station
    )

# Passing stop class
class PassingStop(Stop):
  # Constructor
  def __init__(self, **kwargs):
    self.station = kwargs.get('station')
    self.arrival_time = None
    self.arrival_platform = ''
    self.departure_time = None
    self.departure_platform = ''

# Service class
class Service:
  # Constructor
  def __init__(self, **kwargs):
    self.id = kwargs.get('id')
    self.company = kwargs.get('company')
    self.service_number = kwargs.get('service_number')
    self.variant = kwargs.get('variant')
    self.service_name = kwargs.get('service_name')
    self.footnote = kwargs.get('footnote')
    self.transport_mode = kwargs.get('transport_mode')
    self.attributes = kwargs.get('attributes') or []
    self.stops = kwargs.get('stops') or []

  # Convert to string
  def __str__(self):
    return "{} {} {}to {} {}".format(
      self.company,
      self.transport_mode,
      (str(self.service_number) + ' ') if self.service_number != 0 else '',
      self.stops[-1].station,
      ("(" + ", ".join(str(attribute) for attribute in self.attributes) + ")") if self.attributes else ''
    )

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
      departure_time = parse_time(string[9:13])
    )

# Stop with direct continuation record class
class ContinuationRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip()),
      time = parse_time(string[9:13])
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
      arrival_time = parse_time(string[9:13]),
      departure_time = parse_time(string[14:18])
    )

# Last stop record class
class FinalRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      station = context.stations.get(string[1:8].strip()),
      arrival_time = parse_time(string[9:13])
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

# Timetable file
class TimetableFile(File, list):
  # Constructor
  def __init__(self, identification_record):
    super(TimetableFile,self).__init__(identification_record)

  # Split a service in multiple services
  def split_services(self, service_record):
    # For each service add a service to the file
    for service_number_record in service_record.service_numbers:
      # Create a new service
      service = Service(
        id = service_record.id,
        company = service_number_record.company,
        service_number = service_number_record.service_number,
        variant = service_number_record.variant,
        service_name = service_number_record.service_name,
        footnote = service_record.footnote,
        transport_mode = service_record.transport_mode,
        attributes = service_record.attributes,
        stops = service_record.stops
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
            timetable_file.split_services(current_service)

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

        elif type(record) in [StartRecord, ContinuationRecord, IntervalRecord, FinalRecord]:
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the stop
          current_stop = Stop(**record.__dict__)
          current_service.stops.append(current_stop)

        elif isinstance(record,PassingRecord):
          # Check if a service is selected
          if current_service is None:
            raise RuntimeError("No service is selected")

          # Append the stop
          current_stop = PassingStop(**record.__dict__)
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
        timetable_file.split_services(current_service)

      # Return the file
      return timetable_file
