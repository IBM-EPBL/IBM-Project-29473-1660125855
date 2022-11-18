import os
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

message = Mail(
    from_email = 'mjeevan5791@gmail.com',  
    to_emails = 'jeffreylawrence2121@gmail.com',
    subject = 'Sending with SendGrid is Fun',
    html_content = '<strong>and easy to do anywhere, even with Python</strong>')

try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)
