from . import base, rsscommon
import html, datetime, re

class Feeder(base.Feeder):
    def __iter__(self):
        for n, i in self.feeds.items():
            assert 'url' in i
            url = i['url']
            seen = [x for x in self.resource.get(url, [])]
            feed = rsscommon.get_feed(url)
            entries = rsscommon.get_entries(feed)
            content = []
            for e in entries:
                id = rsscommon.get_id(e)
                if id not in seen:
                    links = rsscommon.get_links(e)
                    body = '<p><b>%(title)s</b><br/><font size="-1">%(links)s</font></p>' % {
                        'title':rsscommon.get_title(e),
                        'links':'<br/>'.join(f'<a href="{x}">{html.escape(x)}</a>' for x in links),
                    }
                    if i.get('description', 'no').lower() == 'yes':
                        body += rsscommon.get_content(e)
                    if i.get('strip_images', 'no').lower() == 'yes':
                        body = re.sub(r'<img\b.*?/?>', '', body)
                    if i.get('strip_iframes', 'no').lower() == 'yes':
                        body = re.sub(r'<iframe\b.*?>.*?</iframe>', '',
                               re.sub(r'<iframe\b.*?/>', '', body))
                    if i.get('strip_empty_links', 'no').lower() == 'yes':
                        body = re.sub(r'<a\s[^>]*></a>', '', body,
                            flags=re.MULTILINE)
                    if i.get('dedupe_brs', 'no').lower() == 'yes':
                        body = re.sub(r'<br\s*/?>\s*<br\s*/?>(\s*<br\s*/?>)+',
                            '<br/>', body, flags=re.MULTILINE)
                    content.append(body)
                    seen.append(id)
            if len(content) > 0:
                yield base.Entry(n, '%s summary (%s)' % (n,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M')),
                    '<hr/>'.join(content), html=True)
            self.resource[url] = seen
            yield base.SyncRequest()
