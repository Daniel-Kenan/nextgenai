import unittest
from flask_testing import TestCase
from flask_socketio import SocketIOTestClient
from server import app, socketio

class TestServer(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        self.client = self.app.test_client()
        self.socketio_client = SocketIOTestClient(app, socketio)

    def tearDown(self):
        self.socketio_client.disconnect()

    def test_http_endpoint(self):
        response = self.client.get('/', query_string={'accesstoken': '222001313@ump.ac.za', 'question': 'What is AI?'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json)

    def test_http_endpoint_invalid_token(self):
        response = self.client.get('/', query_string={'accesstoken': 'invalid_token', 'question': 'What is AI?'})
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json)

    def test_websocket_connection(self):
        self.socketio_client.emit('message', 'Hello')
        received = self.socketio_client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['name'], 'response')

    def test_websocket_invalid_origin(self):
        headers = {'Origin': 'http://invalid-origin.com'}
        self.socketio_client.connect(headers=headers)
        self.assertFalse(self.socketio_client.is_connected)

if __name__ == '__main__':
    unittest.main()
