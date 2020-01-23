from app import mail
from app.utilities.email import send_email, send_async_email
import pytest


def test_sendEmail(test_app, baseMail):
    with mail.record_messages() as outbox:
        send_email(subject=baseMail['subject'],
                   sender=baseMail['sender'],
                   recipients=baseMail['recipients'],
                   cc=baseMail['cc'],
                   text_body=baseMail['text_body'],
                   html_body=baseMail['html_body'])
        assert len(outbox) == 1
        msg = outbox[0]
        assert msg.subject == 'Test'
        assert "hello world!" in msg.body
        assert "<p>hello world!<p>" in msg.html
        assert "test@test.com" in msg.recipients
        assert "test2@test.com" in msg.cc
 