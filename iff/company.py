from iff import Record, DictFile
from iff.delivery import IdentificationRecord

# COmpany record class
class CompanyRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      id = int(string[0:3]),
      code = string[4:14].strip(),
      name = string[15:45].strip(),
      time = int(string[46:50])
    )

  # Convert to string
  def __str__(self):
    return self.name

# Company file class
class CompanyFile(DictFile):
  # Constructor
  def __init__(self, identification_record):
    super(CompanyFile,self).__init__(identification_record)

  # Read a file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new file
      identification_record = IdentificationRecord.read(next(file),context)
      company_file = cls(identification_record)

      # Iterate over the file
      for string in file:
        record = CompanyRecord.read(string,context)
        company_file.append(record)

      # Return the file
      return company_file
