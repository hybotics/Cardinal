from xml.dom import minidom
import urllib2
import logging

from cardinal.decorators import command, help

WHERE_API_APP_ID = "MoToWJjdQX4XzV34ELXxh3MLG5x1cgBMiMrEuJ." \
                   "0D_bohsdQlv5p7qzQXLgXmWID_zPRxFULW454h3"
WHERE_API_URL = "http://where.yahooapis.com/v1/places.q(%s);count=1?appid=" + \
                WHERE_API_APP_ID
WHERE_API_NS = "http://where.yahooapis.com/v1/schema.rng"
WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?w=%s'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'


class WeatherPlugin(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @command('weather', 'w')
    @help("Retrieves the weather using the Yahoo! weather API.",
          "Syntax: .weather <location>")
    def get_weather(self, cardinal, user, channel, msg):
        try:
            location = msg.split(' ', 1)[1]
        except IndexError:
            cardinal.sendMsg(channel, "Syntax: .weather <location>")
            return

        try:
            url = WHERE_API_URL % urllib2.quote(location)
            dom = minidom.parse(urllib2.urlopen(url))
        except Exception:
            cardinal.sendMsg(channel, "Error accessing Yahoo! Where API.")
            self.logger.exception("Error occurred accessing Yahoo! Where API")
            return

        try:
            woeid = str(dom.getElementsByTagNameNS(WHERE_API_NS, 'woeid')[0].
                        firstChild.nodeValue)
        except IndexError:
            cardinal.sendMsg(
                channel, "Sorry, couldn't find weather for '%s'." % location)
            self.logger.warning("No WOEID found for '%s'" % location)
            return

        try:
            url = WEATHER_URL % urllib2.quote(woeid)
            dom = minidom.parse(urllib2.urlopen(url))
        except Exception:
            cardinal.sendMsg(channel, "Error accessing Yahoo! Weather API.")
            self.logger.exception(
                "Error occurred accessing Yahoo! Weather API")
            return

        try:
            ylocation = dom.getElementsByTagNameNS(WEATHER_NS, 'location')[0]
            yunits = dom.getElementsByTagNameNS(WEATHER_NS, 'units')[0]
            ywind = dom.getElementsByTagNameNS(WEATHER_NS, 'wind')[0]
            yatmosphere = dom.getElementsByTagNameNS(
                WEATHER_NS, 'atmosphere')[0]
            ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]

            location_city = str(ylocation.getAttribute('city'))
            location_region = str(ylocation.getAttribute('region'))
            location_country = str(ylocation.getAttribute('country'))

            current_condition = str(ycondition.getAttribute('text'))
            current_temperature = str(ycondition.getAttribute('temp'))
            current_humidity = str(yatmosphere.getAttribute('humidity'))
            current_wind_speed = str(ywind.getAttribute('speed'))

            units_temperature = str(yunits.getAttribute('temperature'))
            units_speed = str(yunits.getAttribute('speed'))

            if units_temperature == "F":
                units_temperature2 = "C"
                current_temperature2 = str(int(
                    (float(current_temperature) - 32) * float(5)/float(9)))
            else:
                units_temperature2 = "F"
                current_temperature2 = str(int(
                    float(current_temperature) * float(9)/float(5) + 32))

            location = location_city
            if location_region:
                location += ", " + location_region
            if location_country:
                location += ", " + location_country

            cardinal.sendMsg(channel,
                             "[ %s | %s | Temp: %s %s (%s %s) | "
                             "Humidity: %s%% | Winds: %s %s ]" % (
                                 location,
                                 current_condition,
                                 current_temperature, units_temperature,
                                 current_temperature2, units_temperature2,
                                 current_humidity,
                                 current_wind_speed, units_speed))
        except IndexError:
            cardinal.sendMsg(
                channel, "Sorry, couldn't find weather for '%s'." % location)
            self.logger.exception(
                "Missing weather information for '%s'" % location)
            return


def setup():
    return WeatherPlugin()
