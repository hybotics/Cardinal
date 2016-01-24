import functools


def command(triggers):
    if isinstance(triggers, basestring):
        triggers = [triggers]

    if not isinstance(triggers, list):
        raise TypeError("Command must be a trigger string or list of triggers")

    def wrap(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        inner.commands = triggers
        return inner

    return wrap


def help(*lines):
    def wrap(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        # Create help list or prepend to it
        if not hasattr(inner, 'help'):
            inner.help = lines
        else:
            inner.help = lines + inner.help

        return inner

    return wrap


def event(triggers):
    if isinstance(triggers, basestring):
        triggers = [triggers]

    if not isinstance(triggers, list):
        raise TypeError("Event must be a trigger string or list of triggers")

    def wrap(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        inner.events = triggers
        return inner

    return wrap
