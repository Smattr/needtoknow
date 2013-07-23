import smtplib
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

    def send(self, name, title, body):
        assert self.conn is not None
        m = MIMEText(body, 'plain', _charset='utf-8')
        m['To'] = self.opts['to']
        m['From'] = '%s <%s>' % (name, self.opts['from'])
        m['Subject'] = title
        self.conn.sendmail(self.opts['from'], self.opts['to'], m.as_string())
