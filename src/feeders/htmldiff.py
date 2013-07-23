import base
import difflib, urllib2

class Feeder(base.Feeder):
    def __iter__(self):
        for i in self.items:
            assert 'url' in i
            url = i['url']
            if url in self.resource:
                old = self.resource[url].splitlines()
            else:
                old = []
            response = urllib2.urlopen(url)
            new = response.read().splitlines()
            content = '\n'.join(list(difflib.unified_diff(old, new, lineterm='')))
            if content:
                yield 'Changes to %(url)s:\n\n%(content)s' % {
                    'url':url,
                    'content':content,
                }
            self.resource[url] = '\n'.join(new)
