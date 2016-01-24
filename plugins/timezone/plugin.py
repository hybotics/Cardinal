from datetime import datetime

from cardinal.decorators import command, help

import pytz
from pytz.exceptions import UnknownTimeZoneError

TIME_FORMAT = '%b %d, %I:%M:%S %p UTC%z'


class TimezonePlugin(object):
    @command('time')
    @help("Gives the current time in a timezone (e.g. -5 or America/Detroit)",
          "Syntax: .time <timezone>")
    def get_time(self, cardinal, user, channel, msg):
        tz = pytz.utc
        now = datetime.now(tz)

        try:
            tz_input = msg.split(' ', 1)[1].strip()
        except IndexError:
            return cardinal.sendMsg(channel,
                                    now.strftime(TIME_FORMAT))

        offset = None
        try:
            offset = int(tz_input)
        except ValueError:
            pass

        try:
            if offset is not None:
                # flip the - sign on the timezones
                if offset < 0:
                    tz = pytz.timezone('Etc/GMT+{0}'.format(offset * -1))
                elif offset > 0:
                    tz = pytz.timezone('Etc/GMT{0}'.format(offset * -1))
            else:
                tz = pytz.timezone(tz_input)
        except UnknownTimeZoneError:
            return cardinal.sendMsg(channel, 'Invalid timezone')

        cardinal.sendMsg(channel, tz.normalize(now).strftime(TIME_FORMAT))


def setup():
    return TimezonePlugin()
