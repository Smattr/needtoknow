#!/usr/bin/env python

import os, sys
import config, pickler

_PATH_APPENDED = False
def construct_feeder(name):
    global _PATH_APPENDED
    if not _PATH_APPENDED:
        sys.path.insert(0, os.path.join(os.curdir, 'feeders'))
        _PATH_APPENDED = True

    try:
        mod = __import__(name)
    except Exception as e:
        print >>sys.stderr, 'Warning: failed to import feeder %s: %s' % (name, e)
        return None

    respath = os.path.join(os.path.expanduser('~'), '.needtoknow/cache/%s.pickle' % name)
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

    return 0

if __name__ == '__main__':
    sys.exit(main())
