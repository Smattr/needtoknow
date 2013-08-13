import smtplib
from email.mime.multipart import MIMEMultipart
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
        if entry.html:
            m = MIMEMultipart('alternative')
            part = MIMEText(entry.content, 'html', _charset='utf-8')
            m.attach(part)
        else:
            m = MIMEText(entry.content, 'plain', _charset='utf-8')
        m['To'] = self.opts['to']
        m['From'] = '%s <%s>' % (entry.name, self.opts['from'])
        m['Subject'] = '[%s] %s' % (entry.name, entry.subject)
        if entry.date:
            m['Date'] = entry.date
        self.conn.sendmail(self.opts['from'], self.opts['to'], m.as_string())
