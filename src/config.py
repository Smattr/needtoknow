import ConfigParser, os

def _get_parser(path):
    p = ConfigParser.SafeConfigParser()

    with open(path, 'r') as f:
        p.readfp(f)

    return p

def get_config(path=None):
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.needtoknow/conf.ini')
    return _get_parser(path)

def get_feeds(path=None):
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.needtoknow/feeds.ini')
    return _get_parser(path)
