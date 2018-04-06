from iff import Record, DictFile
from iff.delivery import IdentificationRecord

# Footnote record class
class FootnoteRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      id = int(string[1:6]),
      first_day = context.delivery.identification_record.first_day,
      last_day = context.delivery.identification_record.last_day,
    )

  # Return if a date is valid
  def valid_on(self, date):
    # Check if the date is in range
    if date < self.first_day or date > self.last_day:
      return False

    # Calculate the difference
    diff = (date - self.first_day).days
    return self.vector[diff]

  # Convert to string
  def __str__(self):
    return self.__class__.__name__

# Vector record class
class VectorRecord(Record):
  # Read a record from a string
  @classmethod
  def read(cls, string, context):
    return cls(
      vector = [character == '1' for character in string]
    )

# Record identifiers
identifiers = {
  '#': FootnoteRecord
}

# Footnote file class
class FootnoteFile(DictFile):
  # Constructor
  def __init__(self, identification_record):
    super(FootnoteFile,self).__init__(identification_record)

  # Read a footnote file
  @classmethod
  def read(cls, file_name, context):
    # Open the file
    with open(file_name) as file:
      # Create a new footnote file
      identification_record = IdentificationRecord.read(next(file),context)
      footnote_file = cls(identification_record)

      # Initialize local variables
      current_footnote = None

      # Iterate over the file
      for string in file:
        # Get the record belonging to the identifier and parse it
        identifier = string[0]
        if identifier not in identifiers:
          record = VectorRecord.read(string,context)
        else:
          record = identifiers.get(identifier).read(string,context)

        # Switch the record
        if isinstance(record,FootnoteRecord):
          # Check if a footnote is selected, then add it
          if current_footnote is not None:
            footnote_file.append(current_footnote)

          # Create a new footnote
          current_footnote = record

        elif isinstance(record,VectorRecord):
          # Check if a footnote is selected
          if current_footnote is None:
            raise RuntimeError("No footnote is selected")

          # Set the vector
          current_footnote.vector = record.vector

      # Append the last footnote
      if current_footnote is not None:
        footnote_file.append(current_footnote)

      # Return the file
      return footnote_file
