from cardinal.decorators import command, help


class AdminPlugin(object):
    # A dictionary which will contain the owner nicks and vhosts
    owners = None

    # A list of trusted vhosts
    trusted_vhosts = None

    def __init__(self, cardinal, config):
        self.owners = {}
        self.trusted_vhosts = []

        # If owners aren't defined, bail out
        if 'owners' not in config:
            return

        # Loop through the owners in the config file and add them to the
        # instance's owner array.
        for owner in config['owners']:
            owner = owner.split('@')
            self.owners[owner[0]] = owner[1]
            self.trusted_vhosts.append(owner[1])

    # A command to quickly check whether a user has permissions to access
    # these commands.
    def is_owner(self, user):
        _, _, vhost = user
        if vhost in self.trusted_vhosts:
            return True

        return False

    @command('eval')
    @help("A dangerous command that runs eval() on the input. (admin only)",
          "Syntax: .eval <command>")
    def eval(self, cardinal, user, channel, msg):
        if not self.is_owner(user):
            return

        command = ' '.join(msg.split()[1:])
        if len(command) == 0:
            return

        try:
            output = str(eval(command))
            cardinal.sendMsg(channel, output)
        except Exception, e:
            cardinal.sendMsg(channel, 'Exception %s: %s' %
                                      (e.__class__, e))
            raise

    @command('exec')
    @help("A dangerous command that runs exec() on the input. (admin only)",
          "Syntax: .exec <command>")
    def execute(self, cardinal, user, channel, msg):
        if not self.is_owner(user):
            return
        command = ' '.join(msg.split()[1:])
        if len(command) == 0:
            return

        try:
            exec(command)
            cardinal.sendMsg(channel, "Ran exec() on input.")
        except Exception, e:
            cardinal.sendMsg(channel, 'Exception %s: %s' %
                                      (e.__class__, e))
            raise

    @command('load', 'reload')
    @help("If no plugins are given after the command, reload all plugins.",
          "Otherwise, load (or reload) the selected plugins. (admin only)",
          "Syntax: .reload [plugin [plugin ...]]")
    def load_plugins(self, cardinal, user, channel, msg):
        nick, _, _ = user

        if not self.is_owner(user):
            return

        cardinal.sendMsg(channel, "%s: Loading plugins..." % nick)

        plugins = msg.split()
        plugins.pop(0)

        if len(plugins) == 0:
            plugins = []
            for plugin in cardinal.plugin_manager:
                plugins.append(plugin['name'])

        failed = cardinal.plugin_manager.load(plugins)

        successful = [
            plugin for plugin in plugins if plugin not in failed
        ]

        if len(successful) > 0:
            cardinal.sendMsg(channel, "Plugins loaded succesfully: %s." %
                                      ', '.join(sorted(successful)))

        if len(failed) > 0:
            cardinal.sendMsg(channel, "Plugins failed to load: %s." %
                                      ', '.join(sorted(failed)))

    @command('unload')
    @help("Unload the selected plugins. (admin only)",
          "Syntax: .unload <plugin [plugin ...]>")
    def unload(self, cardinal, user, channel, msg):
        nick, _, _ = user

        if not self.is_owner(user):
            return

        plugins = msg.split()
        plugins.pop(0)

        if len(plugins) == 0:
            cardinal.sendMsg(channel, "%s: No plugins to unload." % nick)
            return

        cardinal.sendMsg(channel, "%s: Unloading plugins..." % nick)

        # Returns a list of plugins that weren't loaded to begin with
        unknown = cardinal.plugin_manager.unload(plugins)
        successful = [
            plugin for plugin in plugins if plugin not in unknown
        ]

        if len(successful) > 0:
            cardinal.sendMsg(channel, "Plugins unloaded succesfully: %s." %
                                      ', '.join(sorted(successful)))

        if len(unknown) > 0:
            cardinal.sendMsg(channel, "Unknown plugins: %s." %
                                      ', '.join(sorted(unknown)))

    @command('disable')
    @help("Disable plugins in a channel. (admin only)",
          "Syntax: .disable <plugin> <channel [channel ...]>")
    def disable(self, cardinal, user, channel, msg):
        nick, _, _ = user

        if not self.is_owner(user):
            return

        channels = msg.split()
        channels.pop(0)

        if len(channels) < 2:
            cardinal.sendMsg(
                channel, "Syntax: .disable <plugin> <channel [channel ...]>")
            return

        cardinal.sendMsg(channel, "%s: Disabling plugins..." % nick)

        # First argument is plugin
        plugin = channels.pop(0)

        blacklisted = cardinal.plugin_manager.blacklist(plugin, channels)
        if not blacklisted:
            cardinal.sendMsg(channel, "Plugin %s does not exist" % plugin)
            return

        cardinal.sendMsg(channel, "Added to blacklist: %s." %
                                  ', '.join(sorted(channels)))

    @command('enable')
    @help("Enable plugins in a channel. (admin only)",
          "Syntax: .enable <plugin> <channel [channel ...]>")
    def enable(self, cardinal, user, channel, msg):
        nick, _, _ = user

        if not self.is_owner(user):
            return

        channels = msg.split()
        channels.pop(0)

        if len(channels) < 2:
            return cardinal.sendMsg(
                channel, "Syntax: .enable <plugin> <channel [channel ...]>")

        cardinal.sendMsg(channel, "%s: Enabling plugins..." % nick)

        # First argument is plugin
        plugin = channels.pop(0)

        not_blacklisted = cardinal.plugin_manager.unblacklist(plugin, channels)
        if not_blacklisted is False:
            cardinal.sendMsg("Plugin %s does not exist" % plugin)

        successful = [
            chan for chan in channels if chan not in not_blacklisted
        ]

        if len(successful) > 0:
            cardinal.sendMsg(channel, "Removed from blacklist: %s." %
                                      ', '.join(sorted(successful)))

        if len(not_blacklisted) > 0:
            cardinal.sendMsg(channel, "Wasn't in blacklist: %s." %
                                      ', '.join(sorted(not_blacklisted)))

    @command('join')
    @help("Join selected channels. (admin only)",
          "Syntax: .join <channel [channel ...]>")
    def join(self, cardinal, user, channel, msg):
        if not self.is_owner(user):
            return

        channels = msg.split()
        channels.pop(0)
        for channel in channels:
            cardinal.join(channel)

    @command('part')
    @help("Part selected channels. (admin only)",
          "Syntax: .join <channel [channel ...]>")
    def part(self, cardinal, user, channel, msg):
        if not self.is_owner(user):
            return

        channels = msg.split()
        channels.pop(0)
        if len(channels) > 0:
            for channel in channels:
                cardinal.part(channel)
        elif channel != user:
            cardinal.part(channel)

    @command('quit')
    @help("Quits the network with a quit message, if one is defined. "
          "(admin only)",
          "Syntax: .quit [message]")
    def quit(self, cardinal, user, channel, msg):
        if self.is_owner(user):
            cardinal.disconnect(' '.join(msg.split(' ')[1:]))

    @command('dbg_quit')
    @help("Quits the network without setting disconnect flag (for testing "
          "purposes, admin only)",
          "Syntax: .dbg_quit")
    def debug_quit(self, cardinal, user, channel, msg):
        if self.is_owner(user):
            cardinal.quit('Debug disconnect')


def setup(cardinal, config):
    """Returns an instance of the plugin.

    Keyword arguments:
      cardinal -- An instance of Cardinal. Passed in by PluginManager.
      config -- A config for this plugin.
    """
    return AdminPlugin(cardinal, config)
