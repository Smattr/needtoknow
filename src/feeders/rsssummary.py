import base, re, rsscommon

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            seen = self.resource.get(url, set())
            entries = rsscommon.get_entries(url)
            body = ''
            for e in entries:
                id = rsscommon.get_id(e)
                if id not in seen:
                    links = rsscommon.get_links(e)
                    body += '<p><b>%(title)s</b><br/><font size="-1">%(links)s</font></p>' % {
                        'title':e.title,
                        'links':'<br/>'.join(map(lambda x: '<a href="%(link)s">%(link)s</a>' % {'link':x}, links)),
                    }
                    if i.get('description', 'no').lower() == 'yes':
                        body += rsscommon.get_content(e)
                    if i.get('strip_images', 'no').lower() == 'yes':
                        body = re.sub(r'<img.*?/>', '', body)
                    body += '<hr/>'
                    seen.add(id)
            if body:
                yield base.Entry(n, '%s summary' % n, body, html=True)
            self.resource[url] = seen
