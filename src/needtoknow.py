#!/usr/bin/env python

import os, sys
import config, pickler, sender

def get_resource_path(name):
    return os.path.join(os.path.expanduser('~'), '.needtoknow/cache/%s.pickle' % name)

_PATH_APPENDED = False
def construct_feeder(name):
    global _PATH_APPENDED
    if not _PATH_APPENDED:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feeders'))
        _PATH_APPENDED = True

    try:
        mod = __import__(name)
    except Exception as e:
        print >>sys.stderr, 'Warning: failed to import feeder %s: %s' % (name, e)
        return None

    respath = get_resource_path(name)
    if os.path.exists(respath):
        resource = pickler.restore(respath)
    else:
        resource = {}

    return mod.Feeder(resource)

def main():
    try:
        conf = config.get_config()
    except Exception as e:
        print >>sys.stderr, 'Failed to parse config: %s' % e
        return -1

    try:
        feeds = config.get_feeds()
    except Exception as e:
        print >>sys.stderr, 'Failed to parse feeds: %s' % e
        return -1

    feeders = {}

    for s in feeds.sections():
        if feeds.has_option(s, 'feeder') and \
                feeds.get(s, 'feeder') not in feeders:
            f = feeds.get(s, 'feeder')
            if f not in feeders:
                feeders[f] = construct_feeder(f)

        if feeders[f] is not None:
            feeders[f].add(s, dict(feeds.items(s)))

    out = sender.Sender(conf)
    try:
        out.connect()
    except Exception as e:
        print >>sys.stderr, 'Failed to connect to mail server: %s' % e
        return -1

    for f in filter(None, feeders.values()):
        for entry in f:
            try:
                out.send(entry)
            except Exception as e:
                print >>sys.stderr, 'Failed to send update for %s: %s' % (entry.name, e)
                return -1

    out.disconnect()

    # Commit resource changes.
    for f in feeders:
        if feeders[f] is not None:
            respath = get_resource_path(f)
            pickler.save(respath, feeders[f].resource)

    return 0

if __name__ == '__main__':
    sys.exit(main())
