import abc
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional


class Feeder(abc.ABC):
    def __init__(self, resource, log, debug: bool):
        self.resource = resource
        self.feeds = {}
        self.log = log
        self.debug = debug

    def add(self, name, item):
        self.feeds[name] = item

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError


@dataclass
class Entry:
    name: str
    subject: str
    content: str
    date: Optional[str] = None
    html: bool = False


def download(url, log):
    RETRIES = 3
    for i in range(RETRIES):
        try:
            response = urllib.request.urlopen(url, timeout=10)
            return response.read()
        except urllib.error.URLError as e:
            if i == RETRIES - 1:
                log.warning(f"download of {url} failed: {e}")
                raise
            log.warning(f"download of {url} failed (retrying): {e}")
            if getattr(e, "code", None) == 403:
                # Some sites explicitly block urllib to prevent crawling (e.g.
                # Microsoft). Since we're not really a crawler, sidestep this by
                # twiddling our user agent.
                request = urllib.request.Request(url, headers={"User-Agent": ""})
                response = urllib.request.urlopen(request)
                return response.read()


# Sentinel class used by feeders to ask the main logic to write back state to
# disk. Feeders should use this following processing of each feed. The purpose
# of this is to minimise the resending of entries when a feeder is interrupted
# part way through.
class SyncRequest:
    pass
