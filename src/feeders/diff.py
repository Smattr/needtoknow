import diffcommon, base
import difflib, nltk

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
                new = nltk.clean_html(base.download(url).strip()).splitlines()
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
