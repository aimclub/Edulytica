"""
This module provides functionality for sending confirmation emails to users.

Functions:
    send_email: Sends a registration confirmation code to the user's email address.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from edulytica.common.config import SENDER_EMAIL, SENDER_PASSWORD


def send_email(to_email, code):
    """
    Sends a confirmation code via email to the specified recipient.

    This function uses SMTP to send an email containing a registration
    confirmation code to the user's email address. The message includes
    a subject and plain text body with the code.

    Args:
        to_email (str): Recipient's email address.
        code (str): Confirmation code to be included in the message.
    """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = 'Registration Confirmation Code'

    body = f'Hello, your confirmation code for registration on the Edulytica platform is: {code}'
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)

    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, to_email, text)
    server.quit()
