from iff.parser import Record, File, Database
from iff.delivery import IdentificationRecord

# Country record class
class CountryRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      id = string[0:4].strip(),
      inland = bool(string[5:6]),
      name = string[7:37].strip()
    )

  # Convert to string
  def __str__(self):
    return self.name


# Country file class
class CountryFile(File, Database):
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
      country_file = cls(identification_record)

      # Iterate over the file
      for string in file:
        record = CountryRecord.read(string,context)
        country_file.add(record)

      # Return the file
      return country_file
