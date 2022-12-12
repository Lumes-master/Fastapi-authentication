import smtplib
import ssl
import os
from email.message import EmailMessage
from settings import settings

class EmailService:

    def __init__(self):
        self.email_sender = settings.email
        self.email_access = settings.email_access

    def send_reset_code(self,
                        email_receiver: str,
                        reset_code: str ):

        subject = 'reset password'
        body = '''<!DOCTYPE html>
        <html>
#   <head></head>
#   <body>
        <p>
  Hello {user}
</p>
<p>
  Someone has requested a link to change your password, and you can do this through the link below.
</p>
<p>
  <a href="http://127.0.0.1:8000/auth/reset_password"> change password 
  </a>
</p>
<p> To change your password, use {reset_code}
<p>
  If you didn't request this, please ignore this email.
</p>
<p>'
  Your password won't change until you access the link above and create a new one.
</p>
</body>
</html>
'''.format(user=email_receiver, reset_code=reset_code)

        em = EmailMessage()
        em['from'] = self.email_sender
        em['To'] = email_receiver
        em['subject'] = subject
        em.set_content(body, 'html')

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.ukr.net', 465, context=context) as smtp:
            smtp.login(self.email_sender, self.email_access)
            smtp.sendmail(self.email_sender, email_receiver, em.as_string())

# if __name__ == '__main__':
#     email1=EmailService('lumes2017@ukr.net', 'NWoahHXU1BUkDhGu')
#
#     email1.send_reset_code('lumes119@gmail.com', 'code from codealone')