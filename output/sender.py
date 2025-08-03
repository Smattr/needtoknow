import email
import hashlib
import imaplib
import re
import ssl
import time
import urllib.error
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bs4

from feeders.base import download

# Number of bytes to allow embedded images to occupy (after this point, leave
# linked images at their original URLs).
EMBED_THRESHHOLD = 1024 * 1024 * 15


class Sender:
    """
    sending agent for feed entries

    This object takes feed entries and appends them to an IMAP mailbox.

    Args:
        conf: Configuration dict describing how to connect to a mail account.
    """
    def __init__(self, conf):
        self.host = str(conf["host"])
        self.port = str(conf.get("port", "993"))
        self.login = str(conf["login"])
        self.password = str(conf["password"])
        self.folder = str(conf.get("folder", "INBOX"))
        self.conn = None

    def connect(self):
        self.disconnect()
        self.conn = imaplib.IMAP4_SSL(
            self.host, self.port, ssl_context=ssl.create_default_context()
        )
        if self.login is not None:
            self.conn.login(self.login, self.password)

    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            try:
                self.conn.logout()
            except:
                pass
        self.conn = None

    def send(self, entry, log, embed_images):
        assert self.conn is not None

        # If we're sending HTML, try to find and embed any referenced images.
        images = {}
        body = entry.content
        if embed_images and entry.html:
            content = None
            try:
                content = bs4.BeautifulSoup(entry.content, "html.parser")
            except:
                pass
            if content is not None:
                downloaded = 0
                for img in content.findAll("img", src=re.compile("^https?://")):
                    try:
                        data = download(img["src"], log)
                    except (UnicodeEncodeError, urllib.error.URLError):
                        continue
                    downloaded += len(data)
                    if downloaded > EMBED_THRESHHOLD:
                        break
                    try:
                        att = MIMEImage(data)
                    except TypeError:
                        # If we can't guess the MIME subtype, just skip this
                        # one.
                        continue
                    # Generate a Content ID for the image, by which we will
                    # reference it. We use its hash because this gives us a
                    # pseudo globally unique ID (to comply with RFC 2111) while
                    # still being deterministic.
                    cid = hashlib.sha1(data).hexdigest()
                    images[cid] = att
                    img["src"] = f"cid:{cid}"
                body = str(content)

        m = MIMEMultipart("related")
        part = MIMEText(body, "html" if entry.html else "plain", _charset="utf-8")
        m.attach(part)

        # Embed any referenced images.
        for cid, att in images.items():
            att.add_header("Content-ID", f"<{cid}>")
            m.attach(att)

        m["To"] = "Me" if self.login is None else self.login
        # Make the sender look like a valid email if it does not already. This
        # has no effect in most email clients, but the GMail web and phone apps
        # insist on labelling such emails "unknown sender".
        if re.search(r"<.+@.+>", entry.name) is None:
            m["From"] = f"{entry.name} <example@example.com>"
        else:
            m["From"] = entry.name
        m["Subject"] = entry.subject
        if entry.date:
            stamp = time.mktime(entry.date)
            m["Date"] = email.utils.formatdate(stamp)
        else:
            stamp = time.time()
        log.info('  Sending "%s"...' % entry.subject)
        self.conn.append(
            "INBOX" if self.folder is None else self.folder,
            "",
            imaplib.Time2Internaldate(stamp),
            m.as_string().encode("utf-8", "replace"),
        )
