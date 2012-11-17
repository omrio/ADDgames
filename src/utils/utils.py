def formatMessage(msg):
    if isinstance(msg, basestring):
        return ' '.join(map(str, map(ord, msg)))
    else:
        return repr(msg)
