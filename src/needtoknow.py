#!/usr/bin/env python

import os, sys
import config

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

    print conf

    return 0

    sys.path.insert(0, os.path.join(os.curdir, 'feeders'))
    for i in ['diff', 'htmldiff', 'rss']:
        j = __import__(i)
    f = j.Feeder({}, url='https://www.blah.com')
    for i in f:
        print i

    return 0

if __name__ == '__main__':
    sys.exit(main())
