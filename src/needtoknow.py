#!/usr/bin/env python

import argparse, logging, os, six, sys, urllib2
import sender

def get_resource_path(name):
    return os.path.join(os.path.expanduser('~'), '.needtoknow/cache/%s.pickle' % name)

_PATH_APPENDED = False
def construct_feeder(name, log):
    global _PATH_APPENDED
    if not _PATH_APPENDED:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feeders'))
        _PATH_APPENDED = True

    try:
        mod = __import__(name)
    except Exception as e:
        log.warning('failed to import feeder %s: %s' % (name, e))
        return None

    respath = get_resource_path(name)
    if os.path.exists(respath):
        with open(respath) as f:
            resource = six.moves.cPickle.load(f)
    else:
        resource = {}

    return mod.Feeder(resource)

def online():
    try:
        urllib2.urlopen('http://www.google.com', timeout=5)
        return True
    except urllib2.URLError:
        return False

def main():
    parser = argparse.ArgumentParser('Monitor RSS and other feeds')
    parser.add_argument('--disable', '-d', action='append', default=[],
        help='disable a particular feeder by name')
    parser.add_argument('--enable', '-e', action='append', default=[],
        help='enable a particular feeder by name')
    parser.add_argument('--exclude', '-x', action='append', default=[],
        help='exclude a particular feed by name')
    parser.add_argument('--include', '-i', action='append', default=[],
        help='include a particular feed by name')
    parser.add_argument('--check-connection', action='store_true',
        help='check whether we have an internet connection first')
    opts = parser.parse_args()

    log = logging.getLogger('needtoknow')
    log.addHandler(logging.StreamHandler(sys.stderr))
    # Determine whether we are running interactively.
    if sys.stdout.isatty():
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    if opts.check_connection and not online():
        log.info('no network connection; exiting')
        return 0

    conf = six.moves.configparser.SafeConfigParser()

    try:
        with open(os.path.expanduser('~/.needtoknow/conf.ini')) as f:
            conf.readfp(f)
    except Exception as e:
        log.error('Failed to parse config: %s' % e)
        return -1

    feeds = six.moves.configparser.SafeConfigParser()

    try:
        with open(os.path.expanduser('~/.needtoknow/feeds.ini')) as f:
            feeds.readfp(f)
    except Exception as e:
        log.error('Failed to parse feeds: %s' % e)
        return -1

    feeders = {}

    log.info('Loading feeders...')
    for s in feeds.sections():
        f = feeds.get(s, 'feeder')
        if f not in feeders:
            log.info(' Loading %s...' % f)
            feeders[f] = construct_feeder(f, log)

        if feeders[f] is None:
            log.warning(' Warning: No feeder named %s (referenced by %s).' % (f, s))
        else:
            if s in opts.include or (opts.include == [] and s not in opts.exclude):
                feeders[f].add(s, dict(feeds.items(s)))

    out = sender.Sender(conf)
    try:
        out.connect()
    except Exception as e:
        log.error('Failed to connect to mail server: %s' % e)
        return -1

    log.info('Looking for updates...')
    for f in feeders:
        if feeders[f] is None:
            # We failed to load this feeder.
            continue
        if f in opts.disable or (opts.enable != [] and f not in opts.enable):
            continue
        try:
            log.info(' Scanning %s...' % f)
            for entry in feeders[f]:
                try:
                    out.send(entry)
                except Exception as e:
                    log.error('  Failed to send update for %s: %s' % (entry.name, e))
                    return -1
        except Exception as e:
            log.warning('  Feeder \'%s\' threw exception: %s' % (f, e))

        log.info('  Committing resource changes...')
        # Commit resource changes.
        respath = get_resource_path(f)
        with open(respath, 'wt') as fobj:
            six.moves.cPickle.dump(feeders[f].resource, fobj)

    out.disconnect()

    return 0

if __name__ == '__main__':
    sys.exit(main())
