# from app import create_app
from flask import current_app
from flask_mail import Message
from threading import Thread

from app.extensions import mail


def send_async_email(app, msg):
    # app = create_app()
    print(f"async app {app}")
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """Helper function to send email message."""
    msg = Message(subject, recipients=recipients, sender=sender)
    msg.body = text_body
    msg.html = html_body
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()

