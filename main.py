import iff
import iff.timetable
import random

from datetime import date, timedelta

# Main function
def main():
  tt = iff.IFF('ns-latest')
  today = date(2018,4,13)

  # Print total services
  print("{} total services".format(len(tt.services)))

  # Print valid services
  valid_services = tt.services.filter_valid_on(today)
  print("{} services valid on {}".format(len(valid_services),today))

  # Get services through Utrecht Centraal
  ut = tt.stations.get('ut')
  ut_services = valid_services.map_departs_from(ut)
  print("{} services departing from {}\n".format(len(ut_services.items()),ut))

  for stop, service in ut_services.items():
    print("{:>5}  {:>3}  {}".format(str(stop.departure_time),stop.departure_platform,str(service)))


# Execute the main function
if __name__ == '__main__':
  main()
