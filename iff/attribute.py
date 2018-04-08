from iff.parser import Record, File, Database
from iff.delivery import IdentificationRecord

# Attribute record class
class AttributeRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      id = string[0:4].strip(),
      processing_code = int(string[5:9]),
      description = string[10:40].strip()
    )

  # Convert to string
  def __str__(self):
    return self.description


# Attribute file class
class AttributeFile(File, Database):
  # Constructor
  def __init__(self, identification_record):
    File.__init__(self,identification_record)

  # Read a file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new file
      identification_record = IdentificationRecord.read(next(file),context)
      attribute_file = cls(identification_record)

      # Iterate over the file
      for string in file:
        record = AttributeRecord.read(string,context)
        attribute_file.add(record)

      # Return the file
      return attribute_file
