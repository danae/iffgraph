from collections import OrderedDict

# Stop class
class Stop:
  # Constructor
  def __init__(self, **kwargs):
    self.station = kwargs.get('station')
    self.arrival_time = kwargs.get('time') or kwargs.get('arrival_time')
    self.arrival_platform = (kwargs.get('arrival_platform') or '') if self.arrival_time else ''
    self.departure_time = kwargs.get('time') or kwargs.get('departure_time')
    self.departure_platform = (kwargs.get('departure_platform') or '') if self.departure_time else ''

  # Convert to string
  def __str__(self):
    return "{:<12}  {:<12}  {}".format(
      "A {:<5} {:<4}".format(self.arrival_time,self.arrival_platform) if self.arrival_time else '',
      "D {:<5} {:<4}".format(self.departure_time,self.departure_platform) if self.departure_time else '',
      self.station
    )


# Passing stop class
class PassingStop(Stop):
  # Constructor
  def __init__(self, **kwargs):
    self.station = kwargs.get('station')
    self.arrival_time = None
    self.arrival_platform = ''
    self.departure_time = None
    self.departure_platform = ''


# Service class
class Service:
  # Constructor
  def __init__(self, **kwargs):
    self.id = kwargs.get('id')
    self.company = kwargs.get('company')
    self.service_number = kwargs.get('service_number')
    self.variant = kwargs.get('variant')
    self.service_name = kwargs.get('service_name')
    self.footnote = kwargs.get('footnote')
    self.transport_mode = kwargs.get('transport_mode')
    self.attributes = kwargs.get('attributes') or []
    self.stops = kwargs.get('stops') or []

  # Return is this service is valid on a given date
  def valid_on(self, date):
    return self.footnote.valid_on(date)

  # Return if this service passes a station
  def passes(self, station):
    return station in (stop.station for stop in self.stops)

  # Return the stop if this service passes a station
  def get_passes(self, station):
    try:
      return next(stop for stop in self.stops if stop.station == station)
    except StopIteration:
      return None

  # Return if this service has a departure from a station
  def departs_from(self, station):
    return station in (stop.station for stop in self.stops if stop.departure_time is not None)

  # Return the stop if this service has a departure from a station
  def get_departs_from(self, station):
    try:
      return next(stop for stop in self.stops if stop.station == station and stop.departure_time is not None)
    except StopIteration:
      return None

  # Return if this service has a arrival at a station
  def arrives_at(self, station):
    return station in (stop.station for stop in self.stops if stop.arrival_time is not None)

  # Return the stop if this service has a departure from a station
  def get_arrives_at(self, station):
    try:
      return next(stop for stop in self.stops if stop.station == station and stop.arrival_time is not None)
    except StopIteration:
      return None

  # Convert to string
  def __str__(self):
    return "{} {} {}to {} {}".format(
      self.company,
      self.transport_mode,
      (str(self.service_number) + ' ') if self.service_number != 0 else '',
      self.stops[-1].station,
      ("(" + ", ".join(str(attribute) for attribute in self.attributes) + ")") if self.attributes else ''
    )


# Timetable class
class Timetable(list):
  # Constructor
  def __init__(self, items = []):
    self.extend(items)

  # Get services that qualify to a filter
  def filter(self, filter):
    return Timetable(service for service in self if filter(service))

  # Get services that are valid on a given date
  def filter_valid_on(self, date):
    return self.filter(lambda service: service.valid_on(date))

  # Get services that pass a given station
  def filter_passes(self, station):
    return self.filter(lambda service: service.passes(station))

  # Get services that depart from a given station
  def filter_departs_from(self, station):
    tt = self.filter(lambda service: service.departs_from(station))
    tt.sort(key = lambda service: service.get_departs_from(station).departure_time)
    return tt

  # Get services that arrive from a given station
  def filter_arrives_at(self, station):
    tt = self.filter(lambda service: service.arrives_at(Station))
    tt.sort(key = lambda service: service.get_arrives_at(station).departure_time)
    return tt

  # Map services to a dict with a given key
  def map(self, key):
    d = OrderedDict()
    for service in self:
      d[key(service)] = service
    return d

  # Map services that pass a given station in a dict
  def map_passes(self, station):
    valid_services = self.filter_passes(station)
    return valid_services.map(lambda service: service.get_passes(station))

  # Map services that depart from a given station in a dict
  def map_departs_from(self, station):
    valid_services = self.filter_departs_from(station)
    return valid_services.map(lambda service: service.get_departs_from(station))

  # Map services that arrive at a given station in a dict
  def map_arrives_at(self, station):
    valid_services = self.filter_arrives_at(station)
    return valid_services.map(lambda service: service.get_arrives_at(station))
