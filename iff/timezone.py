from iff import Record, DictFile, parse_date
from iff.delivery import IdentificationRecord

from datetime import timedelta

# Timezone record class
class TimezoneRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string):
    return cls(
      id = int(string[2:5])
    )

# Earlier period record
class EarlierPeriodRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string):
    return cls(
      offset = timedelta(hours = int(string[1:3]) * -1),
      first_day = parse_date(string[4:12]),
      last_day = parse_date(string[13:21])
    )

# Later period record
class LaterPeriodRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string):
    return cls(
      offset = timedelta(hours = int(string[1:3])),
      first_day = parse_date(string[4:12]),
      last_day = parse_date(string[13:21])
    )

# Record identifiers
identifiers = {
  '#': TimezoneRecord,
  '-': EarlierPeriodRecord,
  '+': LaterPeriodRecord
}

# Timezone file class
class TimezoneFile(DictFile):
  # Constructor
  def __init__(self, identification_record):
    super(TimezoneFile,self).__init__(identification_record)

  # Read a file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new file
      identification_record = IdentificationRecord.read(next(file),context)
      timezone_file = cls(identification_record)

      # Initialize local variables
      current_timezone = None

      # Iterate over the file
      for string in file:
        # Get the record belonging to the identifier and parse it
        identifier = string[0]
        if identifier not in identifiers:
          raise RuntimeError('Invalid record type: {}'.format(identifier))

        record = identifiers.get(identifier).read(string)

        # Switch the record
        if isinstance(record,TimezoneRecord):
          # Check if a timezone is selected, then add it
          if current_timezone is not None:
            # Add the timezone to the file
            timezone_file.append(current_timezone)

          # Create a new timezone
          current_timezone = record

        elif isinstance(record,EarlierPeriodRecord) or isinstance(record,LaterPeriodRecord):
          # Check if a timezone is selected
          if current_timezone is None:
            raise RuntimeError("No timezone is selected")

          # Set the period
          current_timezone.offset = record.offset
          current_timezone.first_day = record.first_day
          current_timezone.last_day = record.last_day

      # Append the last timezone
      if current_timezone is not None:
        # Add the timezone to the file
        timezone_file.append(current_timezone)

      # Return the file
      return timezone_file
