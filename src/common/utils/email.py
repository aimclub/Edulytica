"""
This module provides functionality for sending confirmation emails to users.

Functions:
    send_email: Sends a registration confirmation code to the user's email address.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from src.common.config import SENDER_EMAIL, SENDER_PASSWORD, SMTP_PORT, SMTP_SERVER


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
    msg['From'] = formataddr(("Edulytica Security", SENDER_EMAIL))
    msg['To'] = to_email
    msg['Subject'] = 'Registration Confirmation Code'

    body = f'Hello, your confirmation code for registration on the Edulytica platform is: {code}'
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
