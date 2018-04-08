from iff.delivery import DeliveryFile
from iff.service import ServiceFile
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
    self.services = ServiceFile.read("{}/timetbls.dat".format(directory),self)
    if not self.services.is_valid(self.delivery):
      raise RuntimeException("The TIMETBLS file is not valid")
