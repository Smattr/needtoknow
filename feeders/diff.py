import difflib

import bs4

from . import base, diffcommon


class Feeder(base.Feeder):
    """an entry generator that produces diffs between two files"""
    def __iter__(self):
        for n, i in self.feeds.items():
            assert "url" in i
            url = i["url"]
            if url in self.resource:
                old = self.resource[url].splitlines()
                oldurl = url
            else:
                old = []
                oldurl = "/dev/null"
            try:
                new = (
                    bs4.BeautifulSoup(base.download(url, self.log).strip(), "html.parser")
                    .get_text()
                    .splitlines()
                )
            except Exception as e:
                yield Exception(f"Error while loading {url}: {e}")
                continue
            lines = list(
                difflib.unified_diff(old, new, fromfile=oldurl, tofile=url, lineterm="")
            )
            if i.get("ignore_white_space", "yes").lower() == "yes":
                lines = list(diffcommon.suppress_whitespace(lines))
            if len(lines) > 2:
                content = "\n".join(lines)
                yield base.Entry(n, f"{url} changes", content)
            self.resource[url] = "\n".join(new)
            yield base.SyncRequest()
