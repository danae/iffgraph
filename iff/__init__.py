from datetime import datetime, timedelta
from collections import OrderedDict

# Time base class
class Time(timedelta):
  # New object
  def __new__(self, hours, minutes):
    return timedelta.__new__(self, hours = hours, minutes = minutes)

  # Convert to string
  def __str__(self):
    hours = int(self.seconds / 3600)
    minutes = int(self.seconds / 60 % 60)
    return "{:d}:{:02d}".format(hours % 24,minutes)

# Parse a date string in DDMMYYYY format
def parse_date(string):
  return datetime.strptime(string,'%d%m%Y').date()

# Parse a time string in HHMM format with lenient hours
def parse_time(string):
  hours = int(string[0:2])
  minutes = int(string[2:4])
  return Time(hours,minutes)

# Record base class
class Record:
  # Constructor
  def __init__(self, **kwargs):
    self.__dict__.update(**kwargs)

  # Check if two records are equal
  def __eq__(self, other):
    return type(self) == type(other) and self.__dict__ == other.__dict__

  # Convert to string
  def __str__(self):
    return "{}: {}".format(self.__class__.__name__,self.__dict__)

# File base class
class File:
  # Constructor
  def __init__(self, identification_record):
    self.identification_record = identification_record

  # Return if another file is valid
  def is_valid(self, other):
    return self.identification_record == other.identification_record

# File with dictionary base class
class DictFile(File, OrderedDict):
  # Constructor
  def __init__(self, identification_record, id_field = 'id'):
    super(DictFile,self).__init__(identification_record)
    self.id_field = id_field

  # Add a record
  def append(self, record):
    self[record.__dict__[self.id_field]] = record

  # Add multiple records
  def extend(self, records):
    for record in records:
      self.append(record)


from iff.delivery import DeliveryFile
from iff.timetable import TimetableFile
from iff.footnote import FootnoteFile
from iff.station import StationFile
from iff.transport_mode import TransportModeFile
from iff.country import CountryFile
from iff.company import CompanyFile
from iff.attribute import AttributeFile
from iff.timezone import TimezoneFile

# IFF main class
class IFF:
  # Constructor
  def __init__(self, directory):
    # Read the DELIVERY file
    self.delivery = DeliveryFile.read("{}/delivery.dat".format(directory),self)

    # Read the TRNSATTR file
    self.attributes = AttributeFile.read("{}/trnsattr.dat".format(directory),self)
    if not self.attributes.is_valid(self.delivery):
      raise RuntimeException("The TRNSATTR file is not valid")

    # Read the TIMEZONE file
    self.timezones = TimezoneFile.read("{}/timezone.dat".format(directory),self)
    if not self.timezones.is_valid(self.delivery):
      raise RuntimeException("The TIMEZONE file is not valid")

    # Read the COUNTRY file
    self.countries = CountryFile.read("{}/country.dat".format(directory),self)
    if not self.countries.is_valid(self.delivery):
      raise RuntimeException("The COUNTRY file is not valid")

    # Read the COMPANY file
    self.companies = CompanyFile.read("{}/company.dat".format(directory),self)
    if not self.companies.is_valid(self.delivery):
      raise RuntimeException("The COMPANY file is not valid")

    # Read the STATIONS file
    self.stations = StationFile.read("{}/stations.dat".format(directory),self)
    if not self.stations.is_valid(self.delivery):
      raise RuntimeException("The STATIONS file is not valid")

    # Read the FOOTNOTE file
    self.footnotes = FootnoteFile.read("{}/footnote.dat".format(directory),self)
    if not self.footnotes.is_valid(self.delivery):
      raise RuntimeException("The FOOTNOTE file is not valid")

    # Read the TRNSMODE file
    self.transport_modes = TransportModeFile.read("{}/trnsmode.dat".format(directory),self)
    if not self.transport_modes.is_valid(self.delivery):
      raise RuntimeException("The TRNSMODE file is not valid")

    # Read the TIMETBLS file
    self.services = TimetableFile.read("{}/timetbls.dat".format(directory),self)
    if not self.services.is_valid(self.delivery):
      raise RuntimeException("The TIMETBLS file is not valid")
