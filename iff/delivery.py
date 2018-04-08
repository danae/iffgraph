from iff.parser import Date, Record, File

# Identification record class
class IdentificationRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      company_number = int(string[1:4]),
      first_day = Date.parse(string[5:13]),
      last_day = Date.parse(string[14:22]),
      version_number = int(string[23:27]),
      description = string[28:58].strip()
    )

# Delivery file class
class DeliveryFile(File):
  # Constructor
  def __init__(self, identification_record):
    super(DeliveryFile,self).__init__(identification_record)

  # Read a DELIVERY file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      identification_record = IdentificationRecord.read(next(file),context)
      return cls(identification_record)
