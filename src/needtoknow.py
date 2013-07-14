#!/usr/bin/env python

import os, pickle, sys

def save(filename, obj):
    with open(filename, 'w') as f:
        pickle.dump(obj, f)

def restore(filename):
    with open(filename, 'r') as f:
        return pickle.load(f)

def main():
    sys.path.insert(0, os.path.join(os.curdir, 'feeders'))
    for i in ['diff', 'htmldiff', 'rss']:
        j = __import__(i)
    f = j.Feeder({}, url='https://www.blah.com')
    for i in f:
        print i

    return 0

if __name__ == '__main__':
    sys.exit(main())
