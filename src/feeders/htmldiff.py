import base
import difflib, urllib2

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            if url in self.resource:
                old = self.resource[url].splitlines()
                oldurl = url
            else:
                old = []
                oldurl = '/dev/null'
            response = urllib2.urlopen(url)
            new = response.read().strip().splitlines()
            content = '\n'.join(list(difflib.unified_diff(old, new,
                fromfile=oldurl, tofile=url, lineterm='')))
            if content:
                yield base.Entry(n, '%s changes' % url, content)
            self.resource[url] = '\n'.join(new)
