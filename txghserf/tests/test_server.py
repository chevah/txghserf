"""
Tests for requests dispatcher.

Functional test using curl:

 curl --data '{"param1": "test"}' \
    -H "X-Github-Event: issue_comment" \
    -H "Content-type: application/json"\
    http://localhost:8080/hook/test

curl --data 'payload=%7B%22key%22%3A%22value%22%7D' \
    -H "X-Github-Event: push" \
    -H "Content-type: application/x-www-form-urlencoded" \
     http://localhost:8080/hook/something

"""
from StringIO import StringIO

from twisted.internet.address import IPv4Address
from twisted.trial.unittest import TestCase
from twisted.web.test.test_web import DummyRequest

from txghserf.server import CONFIGURATION, hook


class TestServer(TestCase):
    """
    Tests for resource handlers.
    """

    def setUp(self):
        super(TestServer, self).setUp()
        self._allowed_ips = CONFIGURATION['allowed_ips'][:]
        self._callback = CONFIGURATION['callback']

        self.request = DummyRequest([])
        ip = '10.0.0.100'
        CONFIGURATION['allowed_ips'].append(ip)
        self.request.client = IPv4Address('TCP', ip, 2345)

    def tearDown(self):
        CONFIGURATION['allowed_ips'] = self._allowed_ips
        CONFIGURATION['callback'] = self._callback
        super(TestServer, self).tearDown()

    def test_hook_bad_ip(self):
        """
        An error is raised when request is comming from an untrusted IP.
        """
        request = DummyRequest([])
        request.client = IPv4Address('TCP', '10.0.0.0', 2345)

        result = hook(request, 'hook_name')

        self.assertEqual(403, request.code)
        self.assertTrue(result.startswith('Error:001: '))

    def test_hook_no_header(self):
        """
        An error is raised when X-Github-Event header is not present.
        """
        result = hook(self.request, 'hook_name')

        self.assertTrue(result.startswith('Error:002: '))

    def test_hook_bad_content_type(self):
        """
        An error is raised when the request has an unsuperted content type.
        """
        self.request.headers['x-github-event'] = 'push'
        self.request.headers['content-type'] = 'unknown'

        result = hook(self.request, 'hook_name')

        self.assertTrue(result.startswith('Error:002: '))

    def test_hook_bad_content(self):
        """
        An error is raised on parser failures.
        """
        self.request.headers['x-github-event'] = 'push'
        self.request.headers['content-type'] = (
            'application/x-www-form-urlencoded')
        self.request.content = StringIO('bad-json-formtat')

        result = hook(self.request, 'hook_name')

        self.assertTrue(result.startswith('Error:003: '))

    def test_hook_all_good_generic_event(self):
        """
        Generic event having json content, are parsed.
        """
        self.called_event = None

        def callbacks(event):
            self.called_event = event

        CONFIGURATION['callback'] = callbacks
        self.request.headers['x-github-event'] = 'issue_comment'
        self.request.headers['content-type'] = 'application/json'
        self.request.content = StringIO('{"key": "value"}')

        result = hook(self.request, 'hook_name')

        self.assertIsNone(result)
        self.assertIsNotNone(self.called_event)
        self.assertEqual('hook_name', self.called_event.hook)
        self.assertEqual('issue_comment', self.called_event.name)
        self.assertEqual({'key': 'value'}, self.called_event.content)

    def test_hook_all_good_push_event(self):
        """
        Push events are parsed from x-www-form-urlencoded.
        """
        self.called_event = None

        def callbacks(event):
            self.called_event = event
        CONFIGURATION['callback'] = callbacks
        self.request.headers['x-github-event'] = 'push'
        self.request.headers['content-type'] = (
            'application/x-www-form-urlencoded')
        self.request.args = {'payload': ['{"key": "value"}']}

        result = hook(self.request, 'hook_name')

        self.assertIsNone(result)
        self.assertIsNotNone(self.called_event)
        self.assertEqual('hook_name', self.called_event.hook)
        self.assertEqual('push', self.called_event.name)
        self.assertEqual({'key': 'value'}, self.called_event.content)
