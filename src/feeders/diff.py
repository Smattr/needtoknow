from . import diffcommon, base
import bs4, difflib

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
                new = bs4.BeautifulSoup(base.download(url).strip()).get_text().splitlines()
            except Exception as e:
                yield Exception('Error while loading %(url)s: %(err)s' % {
                    'url':url,
                    'err':e,
                })
                continue
            lines = list(difflib.unified_diff(old, new, fromfile=oldurl,
                tofile=url, lineterm=''))
            if i.get('ignore_white_space', 'yes').lower() == 'yes':
                lines = list(diffcommon.suppress_whitespace(lines))
            if len(lines) > 2:
                content = '\n'.join(lines)
                yield base.Entry(n, '%s changes' % url, content)
            self.resource[url] = '\n'.join(new)
