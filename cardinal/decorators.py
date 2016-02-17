import functools


def command(*triggers):
    # backwards compatibility
    if len(triggers) == 1 and isinstance(triggers[0], list):
        triggers = tuple(triggers[0])

    def wrap(f):
        f.commands = triggers
        return f

    return wrap


def help(*lines):
    def wrap(f):
        # Create help list or prepend to it
        if not hasattr(f, 'help'):
            f.help = lines
        else:
            f.help = lines + f.help

        return f

    return wrap


def event(triggers):
    if isinstance(triggers, basestring):
        triggers = [triggers]

    if not isinstance(triggers, list):
        raise TypeError("Event must be a trigger string or list of triggers")

    def wrap(f):
        f.events = triggers
        return f

    return wrap
