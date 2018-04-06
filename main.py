import iff
import iff.timetable
import random

from datetime import date, timedelta

# Main function
def main():
  tt = iff.IFF('ns-latest')
  today = date(2018,4,13)

  # Print total services
  print("{} total services".format(len(tt.timetable)))

  # Print valid services
  valid_services = [service for service in tt.timetable if service.footnote.is_valid(today)]
  print("{} services valid on {}".format(len(valid_services),today))

  # Get services through Utrecht Centraal
  ut = tt.stations.get('ut')
  ut_services = [service for service in valid_services if ut in (stop.station for stop in service.stops if not isinstance(stop,iff.timetable.PassingStop) and stop.departure_time is not None)]
  print("{} services departing from {}".format(len(ut_services),ut))
  print()

  ut_services.sort(key = lambda service: next(stop for stop in service.stops if stop.station == ut).departure_time)

  print(" TIME  PLT  TRAIN")
  for service in ut_services:
    at_ut = next(stop for stop in service.stops if stop.station == ut)
    print("{:>5}  {:>3}  {}".format(str(at_ut.departure_time),at_ut.departure_platform,str(service)))


# Execute the main function
if __name__ == '__main__':
  main()
