# from app import create_app
import jwt
from threading import Thread
from time import time

from flask import current_app
from flask_mail import Message

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

def get_token(payload, expiration):
    """Generic function to get jwt token.
    Inputs:
    payload: dict of custom inputs
    expiration: days until expiry
    """
    # convert expiration to seconds
    if expiration is None:
        msg = {}
    else:
        expires_in = expiration * 24 * 60 * 60
        msg = {'exp': time() + expires_in}
    msg.update(payload)
    return jwt.encode(msg, current_app.config['SECRET_KEY'],
                    algorithm='HS256').decode('utf-8')

def decode_token(token, key):
    """Generic function to decode jwt token.
    Inputs:
    token: received by user clicking on emailed link
    key: key that we are using to extract data
    """
    result = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    result = result[key]
    return result