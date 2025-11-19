# src/email_smtp.py
# type: ignore
import smtplib
from email.message import EmailMessage

# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText


def email_reset_password(password):
    from_addr = "email@exemplo.com"
    to_addr = "email@exemplo.com"
    subject = "Assunto do Email"
    body = f"""
A sua nova senha é {password}
"""

    msg = EmailMessage()
    msg.set_content(body)
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject

    # msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("localhost", 8025)
    server.send_message(msg)
    server.quit()
