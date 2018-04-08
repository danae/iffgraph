from datetime import datetime, date, timedelta
from collections import OrderedDict

# Date base class
class Date(date):
  # Return a new instance
  def __new__(cls, year, month, day):
    return date.__new__(cls, year, month, day)

  # Return the date at a given time (Time class)
  def at_time(self, time):
    return datetime.combine(self,time.min + time)

  # Convert to string
  def __str__(self):
    return "{:%Y-%m-%d}".format(self)

  # Parse a DDMMYYYY format
  @classmethod
  def parse(cls, string):
    date = datetime.strptime(string,'%d%m%Y').date()
    return cls(date.year,date.month,date.day)


# Time base class
class Time(timedelta):
  # Return a new instance
  def __new__(cls, hours, minutes):
    return timedelta.__new__(cls, hours = hours, minutes = minutes)

  # Convert to string
  def __str__(self):
    hours = int(self.seconds / 3600)
    minutes = int(self.seconds / 60 % 60)
    return "{:d}:{:02d}".format(hours % 24,minutes)

  # Parse a HHMM format
  @classmethod
  def parse(cls, string):
    hours = int(string[0:2])
    minutes = int(string[2:4])
    return cls(hours,minutes)


# Record base class
class Record:
  # Constructor
  def __init__(self, **kwargs):
    self.__dict__.update(**kwargs)

  # Return if this record equals another record
  def __eq__(self, other):
    return type(self) == type(other) and self.__dict__ == other.__dict__

  # Return the hash for this record
  def __hash__(self):
    return hash((type(self),self.__dict__))

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


# Database base class
class Database(OrderedDict):
  # Constructor
  def __init__(self):
    OrderedDict.__init__(self,identification_record)

  # Add a record
  def add(self, record):
    self[record.id] = record

  # Add multiple records
  def add_multiple(self, records):
    for record in records:
      self.add(record)
