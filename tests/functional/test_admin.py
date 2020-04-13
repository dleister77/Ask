import unittest.mock as mock

from tests.conftest import FunctionalTest


class TestLogin(FunctionalTest):

    routeFunction = 'admin.contactMessage'

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

    @mock.patch('app.admin.routes.send_email')
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

    @mock.patch('app.admin.routes.send_email')
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

