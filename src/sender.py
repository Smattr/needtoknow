import email, imaplib, mimetypes, re, time
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

class Sender(object):
    def __init__(self, conf):
        if conf.has_section('imap'):
            self.opts = dict(conf.items('imap'))
        self.conn = None

    def connect(self):
        self.disconnect()
        self.conn = imaplib.IMAP4_SSL(self.opts['host'], self.opts['port'])
        if 'login' in self.opts:
            self.conn.login(self.opts['login'], self.opts['password'])
        
    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn.logout()
        self.conn = None

    def send(self, entry):
        assert self.conn is not None
        m = MIMEMultipart()
        part = MIMEText(entry.content, 'html' if entry.html else 'plain',
            _charset='utf-8')
        m.attach(part)
        for name, data in entry.files:
            content_type, encoding = mimetypes.guess_type(name)
            if content_type is None or encoding is not None:
                # Unknown content type or compressed.
                content_type = 'application/octet-stream'
            type, subtype = content_type.split('/', 1)
            if type == 'text':
                payload = MIMEText(data, _subtype=subtype)
            elif type == 'image':
                payload = MIMEImage(data, _subtype=subtype)
            elif type == 'audio':
                payload = MIMEAudio(data, _subtype=subtype)
            else:
                # Unknown content.
                payload = MIMEBase(type, subtype)
                payload.set_payload(data)
                encoders.encode_base64(payload)
            payload.add_header('Content-Disposition', 'attachment', filename=name)
            m.attach(payload)
        m['To'] = self.opts.get('login', 'Me')
        # Make the sender look like a valid email if it does not already. This
        # has no effect in most email clients, but the GMail web and phone apps
        # insist on labelling such emails "unknown sender".
        if re.search(r'<.+@.+>', entry.name) is None:
            m['From'] = '%s <example@example.com>' % entry.name
        else:
            m['From'] = entry.name
        m['Subject'] = '[%s] %s' % (entry.name, entry.subject)
        if entry.date:
            stamp = time.mktime(entry.date)
            m['Date'] = email.utils.formatdate(stamp)
        else:
            stamp = time.time()
        self.conn.append(self.opts.get('folder', 'INBOX'), '',
            imaplib.Time2Internaldate(stamp), m.as_string())
