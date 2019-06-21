from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with current_app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Helper function to send email message."""
    msg = Message(subject, recipients=recipients, sender=sender)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email(current_app, msg)).start()
