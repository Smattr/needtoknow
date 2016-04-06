import base
import difflib

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
            try:
                new = base.download(url).strip().splitlines()
            except Exception as e:
                raise Exception('Error while loading %(url)s: %(err)s' % {
                    'url':url,
                    'err':e,
                })
            content = '\n'.join(list(difflib.unified_diff(old, new,
                fromfile=oldurl, tofile=url, lineterm='')))
            if content:
                yield base.Entry(n, '%s changes' % url, content)
            self.resource[url] = '\n'.join(new)
