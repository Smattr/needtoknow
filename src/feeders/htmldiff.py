import base
import difflib, urllib2

class Feeder(base.Feeder):
    def __iter__(self):
        assert 'url' in self.kwargs
        url = self.kwargs['url']
        if url in self.resource:
            old = self.resource[old].splitlines()
        else:
            old = []
        response = urllib2.urlopen(url)
        new = response.read().splitlines()
        yield 'Page not in cache: %(url)s\n\n%(content)s' % {
            'url':url,
            'content':'\n'.join(list(difflib.unified_diff(old, new, lineterm=''))),
        }
        self.resource[url] = '\n'.join(new)
