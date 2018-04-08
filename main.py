import iff
import iff.model
import random

from datetime import date, timedelta

# Main function
def main():
  tt = iff.IFF('ns-latest')
  today = date(2018,4,13)

  # Print total services
  print("{} total services".format(len(tt.services)))

  # Get services through Utrecht Centraal
  ut = tt.stations.get('ut')
  ut_timetable = tt.services.timetable_stops_at(today,ut)
  print("{} services stopping at {} on {:%Y-%m-%d}".format(len(ut_timetable),ut,today))

  for stop, service in ut_timetable:
    # Print service at this station
    if not stop.is_departing():
      print("{:>5} A  {:>3}  {}".format(str(stop.arrival_time),stop.arrival_platform,str(service)))
    else:
      print("{:>5}    {:>3}  {}".format(str(stop.departure_time),stop.departure_platform,str(service)))

    # Print upcoming stops
    for s in service.slice_by_station(start = stop.station).stops:
      if s.station != stop.station and not s.is_passing():
        print("{}{}".format(" " * 16,str(s)))


# Execute the main function
if __name__ == '__main__':
  main()
