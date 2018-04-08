from collections import namedtuple
from copy import copy
from functools import total_ordering
from sortedcontainers import SortedListWithKey


# Stop class
@total_ordering
class Stop:
  # Constructor
  def __init__(self, station, **kwargs):
    self.station = station
    self.arrival_time = kwargs.get('time') or kwargs.get('arrival_time')
    self.arrival_platform = (kwargs.get('arrival_platform') or '') if self.arrival_time else ''
    self.departure_time = kwargs.get('time') or kwargs.get('departure_time')
    self.departure_platform = (kwargs.get('departure_platform') or '') if self.departure_time else ''

  # Return if this stop has a departure
  def is_departing(self):
    return self.departure_time is not None

  # Return if this stop has a arrival
  def is_arriving(self):
    return self.arrival_time is not None

  # Return is this stop does not stop
  def is_passing(self):
    return not self.is_departing() and not self.is_arriving()

  # Return if this stop is equal to another stop
  def __eq__(self, other):
    if not isinstance(other,Stop):
      return False
    elif self.station != other.station:
      return False
    elif self.arrival_time != other.arrival_time:
      return False
    elif self.arrival_platform != other.arrival_platform:
      return False
    elif self.departure_time != other.departure_time:
      return False
    elif self.departure_platform != other.departure_platform:
      return False
    else:
      return True

  # Return a hash for this stop
  def __hash__(self):
    return hash((self.station,self.arrival_time,self.arrival_platform,self.departure_time,self.departure_platform))

  # Compare this stop to another stop
  def __lt__(self, other):
    if not isinstance(other,Stop):
      raise TypeError("Could not compare {} to {}".format(self.__class__.__name__,other.__class__.__name__))
    elif self.station != other.station:
      return self.station.name < other.station.name
    else:
      time_a = self.departure_time or self.arrival_time or None
      time_b = other.departure_time or other.arrival_time or None
      return time_a < time_b

  # Convert to string
  def __str__(self):
    return "{:<12}  {:<10}  {}".format(
      "{:>5} A  {:>3}".format(str(self.arrival_time),self.arrival_platform) if self.arrival_time else '',
      "{:>5}  {:>3}".format(str(self.departure_time),self.departure_platform) if self.departure_time else '',
      str(self.station)
    )

  # Convert to representation
  def __repr__(self):
    return "Stop({})".format(
      ", ".join("{0[0]} = {0[1]}".format(item) for item in self.__dict__.items())
    )


# Service class
class Service:
  # Constructor
  def __init__(self, **kwargs):
    self.id = kwargs.get('id')
    self.company = kwargs.get('company')
    self.variant = kwargs.get('variant')
    self.name = kwargs.get('name')
    self.footnote = kwargs.get('footnote')
    self.transport_mode = kwargs.get('transport_mode')
    self.attributes = kwargs.get('attributes') or []
    self.stops = kwargs.get('stops') or []

  # Slice the stops of this service
  def slice(self, start = None, end = None):
    service = copy(self)
    service.stops = service.stops[start:end]

    service.stops[0].arrival_time = None
    service.stops[0].arrival_platform = ''
    service.stops[-1].departure_time = None
    service.stops[-1].departure_platform = ''

    return service

  # Return the stop if this service has a station
  def get_by_station(self, station):
    try:
      return next(stop for stop in self.stops if stop.station == station)
    except StopIteration:
      return None

  # Slice the stops of this service by station
  def slice_by_station(self, start = None, end = None):
    try:
      start_idx = self.stops.index(self.get_by_station(start)) if start else None
      end_idx = self.stops.index(self.get_by_station(end)) if end else None
      return self.slice(start_idx,end_idx)
    except ValueError as err:
      raise ValueError("This service does not pass the entered station: {}".format(err))

  # Return is this service is valid on a given date
  def valid_on(self, date):
    return self.footnote.valid_on(date)

  # Return if this service has a departure from a station
  def stops_at(self, station):
    return station in (stop.station for stop in self.stops if stop.is_departing() or stop.is_arriving())

  # Return if this service has a departure from a station
  def departs_from(self, station):
    return station in (stop.station for stop in self.stops if stop.is_departing())

  # Return if this service has a arrival at a station
  def arrives_at(self, station):
    return station in (stop.station for stop in self.stops if stop.is_arriving())

  # Return if this service passes a station
  def passes(self, station):
    return station in (stop.station for stop in self.stops if stop.is_passing())

  # Return if this service is equal to another service
  def __eq__(self, other):
    if not isinstance(other,Service):
      return False
    elif self.id != other.id:
      return False
    elif self.company != other.company:
      return False
    elif self.variant != other.variant:
      return False
    elif self.name != other.name:
      return False
    elif self.footnote != other.footnote:
      return False
    elif self.transport_mode != other.transport_mode:
      return False
    elif self.attributes != other.attributes:
      return False
    elif self.stops != other.stops:
      return False
    else:
      return True

  # Return the hash for this service
  def __hash__(self):
    return hash((self.id,self.company,self.variant,self.name,self.footnote,self.transport_mode,self.attributes,self.stops))

  # Convert to string
  def __str__(self):
    return "{} {}{}{} {} -> {}".format(
      self.company,
      self.transport_mode,
      " ({})".format(self.name) if self.name else '',
      " {}".format(self.id) if self.id != 0 else '',
      self.stops[0].station,
      self.stops[-1].station
    )


# Service list class
class ServiceList(list):
  # Constructor
  def __init__(self, items = []):
    self.extend(items)

  # Get services that qualify to a filter
  def filter(self, filter):
    return ServiceList(service for service in self if filter(service))

  # Get services that are valid on a given date
  def filter_valid_on(self, date):
    return self.filter(lambda service: service.valid_on(date))

  # Get services that stop at a given station
  def filter_stops_at(self, station):
    return self.filter(lambda service: service.stops_at(station))

  # Get services that depart from a given station
  def filter_departs_from(self, station):
    return self.filter(lambda service: service.departs_from(station))

  # Get services that arrive at a given station
  def filter_arrives_at(self, station):
    return self.filter(lambda service: service.arrives_at(Station))

  # Get services that pass a given station
  def filter_passes(self, station):
    return self.filter(lambda service: service.passes(Station))

  # Map services that stop at a given station to a timetable
  def timetable_stops_at(self, date, station):
    return Timetable(TimetableItem(service.get_by_station(station),service) for service in self.filter_valid_on(date).filter_stops_at(station))

  # Map services that depart from a given station to a timetable
  def timetable_departs_from(self, date, station):
    return Timetable(TimetableItem(service.get_by_station(station),service) for service in self.filter_valid_on(date).filter_departs_from(station))

  # Map services that arrive at a given station to a timetable
  def timetable_arrives_at(self, date, station):
    return Timetable(TimetableItem(service.get_by_station(station),service) for service in self.filter_valid_on(date).filter_arrives_at(station))


# Timetable item tuple
TimetableItem = namedtuple('TimetableItem',['stop','service'])


# Timetable class
class Timetable(SortedListWithKey):
  # Constructor
  def __init__(self, iterable = None):
    return SortedListWithKey.__init__(self,iterable,lambda item: item.stop)

  # Add two timetables
  def __add__(self, other):
    tt = Timetable()
    tt.update(self)
    tt.update(other)
    return tt
