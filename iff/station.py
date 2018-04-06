from iff import Record, DictFile
from iff.delivery import IdentificationRecord

# Train changes constants
NO_TRAN_CHANGES = 0
TRAN_CHNAGES = 1
VIRTUAL_STATION = 2

# Station record class
class StationRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      train_changes = int(string[0:1]),
      id = string[2:9].strip(),
      change_time = int(string[10:12]),
      maximum_change_time = int(string[13:15]),
      country = context.countries.get(string[16:20].strip()),
      time_zone = context.timezones.get(int(string[21:25])),
      attribute = string[26:28].strip(),
      x_coord = int(string[29:35]),
      y_coord = int(string[36:42]),
      name = string[43:73].strip()
    )

  # Convert to string
  def __str__(self):
    return self.name

# Station file class
class StationFile(DictFile):
  # Constructor
  def __init__(self, identification_record):
    super(StationFile,self).__init__(identification_record)

  # Read a file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new file
      identification_record = IdentificationRecord.read(next(file),context)
      station_file = cls(identification_record)

      # Iterate over the file
      for string in file:
        record = StationRecord.read(string,context)
        station_file.append(record)

      # Return the file
      return station_file
