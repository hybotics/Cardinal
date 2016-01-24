from cardinal.decorators import command, help


class PingPlugin(object):
    @command("ping")
    @help("Responds to a ping message with 'Pong.'",
          "Syntax: .ping")
    def pong(self, cardinal, user, channel, msg):
        nick, _, _ = user
        if channel != nick:
            cardinal.sendMsg(channel, "%s: Pong." % nick)
        else:
            cardinal.sendMsg(channel, "Pong.")


def setup():
    return PingPlugin()
