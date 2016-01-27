#!/usr/bin/env python
import os
import sys

import click

from cardinal.config import ConfigParser

CARDINAL_VERSION = '3.0.0'

# click settings
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'],
                        obj={'STORAGE': None, 'CONFIG': None})


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(CARDINAL_VERSION)
@click.option('--storage', '-s',
              envvar='CARDINAL_STORAGE', type=click.Path(),
              default=os.path.expanduser("~") + "/.cardinal",
              help='Path to storage directory')
@click.pass_context
def cli(ctx, storage):
    """
    Cardinal IRC bot

    A Python IRC bot, with plugin support! Designed to be simple to use, and
    fun to develop with. For information on developing plugins, or more info
    about Cardinal, visit the Github page.

    https://github.com/JohnMaguire/Cardinal
    """
    config = ConfigParser()

    ctx.obj['STORAGE'] = storage
    ctx.obj['CONFIG'] = config

    config.default = {
        'nick': 'Cardinal',
        'plugins': {
            'admin': {'enabled': True},
            'urls': {'enabled': True},
        }
    }

    config.init_directory(os.path.join(storage, 'config'))


@click.command()
@click.argument('network',
                envvar='CARDINAL_NETWORK')
@click.option('--nick', '-n',
              envvar='CARDINAL_NICK',
              help='Nick to connect with')
@click.option('--password', '-p',
              is_flag=True, default=False,
              help='Prompt for NickServ password')
@click.pass_context
def connect(ctx, network, nick, password):
    """
    Connects to a saved network. You may optionally override the default nick
    and NickServ password, or set a custom storage directory path.

    To see the available networks try:

        cardinal network list

    Or for more information about networks:

        cardinal network -h
    """
    storage = ctx.obj['STORAGE']

    # prompt for password if the flag is set, otherwise check to see if it's
    # set in the environment
    if password:
        password = click.prompt("NickServ password", hide_input=True)
    elif 'CARDINAL_PASSWORD' in os.environ:
        password = os.environ['CARDINAL_PASSWORD']

    print network
    print nick
    print password
    print storage
cli.add_command(connect)


@click.group()
def config():
    """
    List and modify config values.

    You can use dot notation to navigate through the config dictionary. Config
    values are set on networks, although network-level defaults can be set
    using the default network. Network configs are merged on top of the default
    config.

    To see all config values:

        cardinal config get

    To set a default config value:

        cardinal config set default.nick Cardinal

    To learn more about networks try:

        cardinal network -h
    """
    pass
cli.add_command(config)


def yield_config(config, prefix=''):
    for key, value in config.items():
        if isinstance(value, dict):
            for key, value in yield_config(value, prefix + key + '.'):
                yield (key, value)
        else:
            yield (prefix + key, value)


def resolve_config(config, setting):
    path = setting.split('.')
    path.reverse()
    while len(path) > 0:
        config = config[path.pop()]

    return config


@click.command(name='set')
@click.argument('setting', required=False)
@click.argument('value', required=False)
@click.pass_context
def config_set(ctx, setting, value):
    prefix = 'default.'

    if setting and setting.strip('.'):
        setting = setting.strip('.')

        # attempt to resolve the config item
        config = resolve_config(ctx.obj['CONFIG'].default, setting)

        # if it's a simple value, print it and exit
        if not isinstance(config, dict):
            click.echo("default.%s = %s" % (setting, config))
            sys.exit(0)

        # otherwise update the prefix for printing, and we'll print all items
        # under the dict
        prefix = prefix + setting + '.'
    else:
        # if no setting is passed, use the defaults
        config = ctx.obj['CONFIG'].default

    for key, val in yield_config(config, prefix=prefix):
        click.echo("%s = %s" % (key, val))

config.add_command(config_set)


@click.command(name='unset')
def config_unset():
    pass
config.add_command(config_unset)


@click.command(name='get')
def config_get():
    pass
config.add_command(config_get)


@click.command(name='append')
def config_append():
    pass
config.add_command(config_append)


@click.command(name='remove')
def config_remove():
    pass
config.add_command(config_remove)


@click.group()
def network():
    """
    List and modify networks.

    Networks are the foundation for configuring Cardinal. A network config
    contains at minimum a single server to connect to. It may also contain a
    nickname to connect to the network with, a NickServ password, and custom
    plugin configuration (including autoload functionality and plugin config.)

    There is also a default network config, which is used as the base config
    for networks -- any settings defined in the default config will be copied
    into the network config for any missing config options.

    To create a network:

        cardinal network create <name>

    To delete a network:

        cardinal network delete <name>
    """
    pass
cli.add_command(network)


@click.command(name='create')
def network_create():
    pass
network.add_command(network_create)


@click.command(name='delete')
def network_delete():
    pass
network.add_command(network_delete)