import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.common.config import SENDER_EMAIL, SENDER_PASSWORD


def send_email(to_email, code):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = 'Код подтверждения регистрации'

    body = f'Здравствуйте, ваш код для подтверждения регистрации на платформе Edulytica: {code}'
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)

    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, to_email, text)
    server.quit()
