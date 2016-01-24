import json
import urllib
import urllib2
import logging

from cardinal.decorators import command, help

MATHJS_API = "http://math.leftforliving.com"


class CalculatorPlugin(object):
    logger = None
    """Logging object for CalculatorPlugin"""

    def __init__(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)

    @command('calc', 'c', 'calculate')
    @help("Calculate using math.js API",
          "Syntax: .calc <query>")
    def calculate(self, cardinal, user, channel, msg):
        nick, _, _ = user

        # Grab the search query
        try:
            question = msg.split(' ', 1)[1]
        except IndexError:
            cardinal.sendMsg(channel, "Syntax: .calc <query>")
            return

        try:
            c_request = {'question': question}
            uh = urllib2.urlopen(MATHJS_API + "/query?" +
                                 urllib.urlencode(c_request))
        except Exception:
            cardinal.sendMsg(channel, "Unable to reach evaluation server.")
            self.logger.exception("Unable to connect to evaluation server")
            return

        try:
            response = json.load(uh)
        except Exception:
            cardinal.sendMsg(channel, "Error parsing API data.")

        if 'error' in response and response['error']:
            cardinal.sendMsg(channel, "Unable to evaluate '%s'." % question)
            self.logger.warning("Unable to evaluate '%s'" % question)
            return

        try:
            answer = response['answer']

            cardinal.sendMsg(channel, "%s: %s = %s" %
                             (nick, str(question), str(answer)))
        except IndexError:
            cardinal.sendMsg(
                channel, "An error occurred while processing the calculation.")


def setup():
    return CalculatorPlugin()
