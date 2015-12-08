import mimetypes, smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

class Sender(object):
    def __init__(self, conf):
        if conf.has_section('smtp'):
            self.opts = dict(conf.items('smtp'))
        self.conn = None

    def connect(self):
        self.disconnect()
        self.conn = smtplib.SMTP(self.opts['host'], self.opts['port'])
        if 'tls' in self.opts and self.opts['tls'].lower() == 'true':
            self.conn.starttls()
        if 'login' in self.opts:
            self.conn.login(self.opts['login'], self.opts['password'])
        
    def disconnect(self):
        if self.conn:
            try:
                self.conn.quit()
            except:
                pass
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
        m['To'] = self.opts['to']
        m['From'] = '%s <%s>' % (entry.name, self.opts['from'])
        m['Subject'] = '[%s] %s' % (entry.name, entry.subject)
        if entry.date:
            m['Date'] = entry.date
        self.conn.sendmail(self.opts['from'], self.opts['to'], m.as_string())
