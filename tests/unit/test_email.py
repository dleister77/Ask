from app import mail
from app.utilities.email import send_email
import pytest


def test_send_email(test_app, base_mail):
    with mail.record_messages() as outbox:
        send_email(subject=base_mail['subject'],
                   sender=base_mail['sender'],
                   recipients=[base_mail['recipients']],
                   text_body=base_mail['text_body'],
                   html_body=base_mail['html_body'])
        assert len(outbox) == 1
        msg = outbox[0]
        assert msg.subject == 'Test'
        assert "hello world!" in msg.body
        print(msg)
        assert "<p>hello world!<p>" in msg.html
        assert "test@test.com" in msg.recipients

