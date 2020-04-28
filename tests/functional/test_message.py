import unittest.mock as mock

from flask import json
from flask_login import current_user

from app.models import Message_User
from tests.conftest import FunctionalTest


class TestContactMessage(FunctionalTest):

    routeFunction = 'message.contactMessage'

    def test_get_anonymous(self, testClient):
        response = self.getRequest(testClient)
        assert response.status_code == 200
        assert b'Ask Your Peeps: Contact Us' in response.data
        assert b'sender_id' not in response.data
        assert b'email' in response.data

    def test_get_authenticated(self, testUser, activeClient):
        response = self.getRequest(activeClient)
        assert response.status_code == 200
        assert b'Ask Your Peeps: Contact Us' in response.data
        assert b'sender_id' in response.data
        assert b'email' not in response.data
        assert testUser.first_name.encode() in response.data
        assert testUser.last_name.encode() in response.data
        assert f'value="{(testUser.id)}"'.encode() in response.data

    @mock.patch('app.message.routes.send_email')
    def test_post_anonymous(self, mock_send_email, testClient):

        self.form = {
            "first_name": "Roberto",
            "last_name": "Firmino",
            "email": "lfirmino@lfc.com",
            "category": "question",
            "subject": "website",
            "body": "what is your name?"
        }
        response = self.postRequest(testClient)
        assert response.status_code == 200
        mock_send_email.assert_called()
        assert b'Message sent'

    @mock.patch('app.message.routes.send_email')
    def test_post_authenticated(self, mock_send_email, testUser, activeClient):

        self.form = {
            "sender_id": testUser.id,
            "first_name": testUser.first_name,
            "last_name": testUser.last_name,
            "category": "question",
            "subject": "website",
            "body": "what is your name?"
        }
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        mock_send_email.assert_called()
        assert b'Message sent'


class TestMessageSend(FunctionalTest):

    routeFunction = 'message.send_message'

    def test_success_new(self, activeClient, testUser2):
        self.form = {
            "subject": "test subject",
            "body": "This is a test message.",
            "recipient_id": testUser2.id,
            "recipient": testUser2.full_name
        }
        u2_inbox = testUser2.get_inbox_unread_count()
        u1_sent = len(current_user.get_messages('sent'))
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        check = {"status": "success"}
        output = json.loads(response.data.decode())
        print(output)
        assert check == output
        assert len(current_user.get_messages('sent')) == u1_sent + 1
        assert testUser2.get_inbox_unread_count() == u2_inbox + 1

    def test_success_reply(self, activeClient, testUser2):
        test_message_id = current_user.get_messages('inbox')[0].id
        u2_inbox = testUser2.get_inbox_unread_count()
        u1_sent = len(current_user.get_messages('sent'))
        self.form = {
            "message_user_id": test_message_id,
            "subject": "test subject",
            "body": "This is a test message.",
            "recipient_id": testUser2.id,
            "recipient": testUser2.full_name
        }
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        check = {"status": "success"}
        output = json.loads(response.data.decode())
        assert check == output
        assert len(current_user.get_messages('sent')) == u1_sent + 1
        assert testUser2.get_inbox_unread_count() == u2_inbox + 1

    def test_error_missing_recipient_id(self, activeClient, testUser2):
        test_message_id = current_user.get_messages('inbox')[0].id
        u2_inbox = testUser2.get_inbox_unread_count()
        u1_sent = len(current_user.get_messages('sent'))
        self.form = {
            "message_user_id": test_message_id,
            "subject": "test subject",
            "body": "This is a test message.",
            "recipient": testUser2.full_name
        }
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        check = {"status": "failure", "errorMsg": "Recipient ID is required"}
        for k, v in check.items():
            assert k, v in response.json.items()

        assert len(current_user.get_messages('sent')) == u1_sent
        assert testUser2.get_inbox_unread_count() == u2_inbox


class TestMessageFolder(FunctionalTest):

    routeFunction = "message.view_messages"

    def test_success_inbox(self, activeClient):
        folder = "inbox"
        response = self.getRequest(activeClient, folder=folder)
        assert response.status_code == 200
        msg = current_user.get_messages('inbox')[0]
        test_message = {
            "id": msg.id,
            "timestamp": msg.message.timestamp,
            "read": msg.read,
            "sender_id": msg.message.sender.user_id,
            "sender_full_name": msg.message.sender.full_name,
            "sender_user_name": msg.message.sender.user.username,
            "status": msg.tag,
            "subject": msg.message.subject,
            "body": msg.message.body
        }
        assert json.dumps(test_message) in response.data.decode()


class TestMessageMove(FunctionalTest):

    routeFunction = "message.move_message"

    def test_move_success(self, activeClient):
        archive_count = len(current_user.get_messages('archive'))
        assert archive_count == 0
        inbox_count = len(current_user.get_messages('inbox'))
        assert inbox_count == 2        
        self.form = {"message_id": 2, "tag": "archive"}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = b"Message archived"
        assert flash in response.data
        archive_count = len(current_user.get_messages('archive'))
        assert archive_count == 1
        inbox_count = len(current_user.get_messages('inbox'))
        assert inbox_count == 1

    def test_move_multiple(self, activeClient):
        archive_count = len(current_user.get_messages('archive'))
        assert archive_count == 0
        inbox_count = len(current_user.get_messages('inbox'))
        assert inbox_count == 2     
        self.form = {"message_id": "2,6", "tag": "archive"}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = b"Messages archived"
        assert flash in response.data
        archive_count = len(current_user.get_messages('archive'))
        assert archive_count == 2
        inbox_count = len(current_user.get_messages('inbox'))
        assert inbox_count == 0

    def test_move_invalid_status(self, activeClient):
        self.form = {"message_id": 2, "tag": "invalid folder name"}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        flash = b"Invalid request.  Please choose a valid folder."
        assert flash in response.data


class TestMessageRead(FunctionalTest):

    routeFunction = "message.message_update_read"

    def test_success(self, activeClient):
        test_case = current_user.get_messages('inbox')[0]
        assert test_case.read is False
        self.form = {"id": test_case.id}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert "status", "success" in response.json.items()
        assert test_case.read is True

    def test_failure(self, activeClient, testUser2):
        test_case = Message_User.query.filter_by(full_name="admin")[0]
        assert test_case.read is False
        self.form = {"id": test_case.id}
        response = self.postRequest(activeClient)
        assert response.status_code == 200
        assert "status", "failure" in response.json.items()
        assert test_case.read is False


class TestMessageGetFriends(FunctionalTest):

    routeFunction = "relationship.get_friends"

    def test_success(self, activeClient):
        test_case = "sa"
        response = self.getRequest(activeClient, name=test_case)
        assert response.status_code == 200
        check = {"id": 1, "full_name": "Sarah Smith"}
        for k, v in check.items():
            assert k, v in response.json.items()

    def test_failure(self, activeClient):
        test_case = "Jim"
        response = self.getRequest(activeClient, name=test_case)
        assert response.status_code == 200
        assert b'[]' in response.data
