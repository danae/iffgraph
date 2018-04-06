from iff import Record, DictFile
from iff.delivery import IdentificationRecord

# Transport mode record
class TransportModeRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      id = string[0:4].strip(),
      description = string[5:35].strip()
    )

  # Convert to string
  def __str__(self):
    return self.description


# Transport mode file
class TransportModeFile(DictFile):
  # Constructor
  def __init__(self, identification_record):
    super(TransportModeFile,self).__init__(identification_record)

  # Read a file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new file
      identification_record = IdentificationRecord.read(next(file),context)
      transport_mode_file = cls(identification_record)

      # Iterate over the file
      for string in file:
        record = TransportModeRecord.read(string,context)
        transport_mode_file.append(record)

      # Return the file
      return transport_mode_file
