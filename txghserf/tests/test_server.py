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

from txghserf.server import CONFIGURATION, expand_allowed_ips, hook


class TestServer(TestCase):
    """
    Tests for resource handlers.
    """

    def setUp(self):
        super(TestServer, self).setUp()
        self._allow_cidr = CONFIGURATION['allow_cidr'][:]
        self._callback = CONFIGURATION['callback']

        self.request = DummyRequest([])
        ip = '10.0.0.100'
        CONFIGURATION['allow_cidr'] = ['10.0.0.0/24']
        expand_allowed_ips()
        self.request.client = IPv4Address('TCP', ip, 2345)

    def tearDown(self):
        CONFIGURATION['allow_cidr'] = self._allow_cidr
        expand_allowed_ips()
        CONFIGURATION['callback'] = self._callback
        super(TestServer, self).tearDown()

    def test_allow_cidr_change_runtime(self):
        """
        When allow_cidr is changed at runtime, `expand_allowed_ips` must
        be called to update the cache.
        """
        CONFIGURATION['allow_cidr'] = [
            '192.30.252.0/22',
            '108.171.174.178/32',
            ]
        expand_allowed_ips()

        self.assertFalse('192.30.251.255' in CONFIGURATION['_allowed_ips'])
        self.assertTrue('192.30.252.0' in CONFIGURATION['_allowed_ips'])
        self.assertTrue('192.30.254.34' in CONFIGURATION['_allowed_ips'])
        self.assertTrue('192.30.255.255' in CONFIGURATION['_allowed_ips'])
        self.assertFalse('192.30.256.0' in CONFIGURATION['_allowed_ips'])

        self.assertFalse('108.171.174.177' in CONFIGURATION['_allowed_ips'])
        self.assertTrue('108.171.174.178' in CONFIGURATION['_allowed_ips'])
        self.assertFalse('108.171.174.179' in CONFIGURATION['_allowed_ips'])

    def test_hook_bad_ip(self):
        """
        An error is raised when request is comming from an untrusted IP.
        """
        request = DummyRequest([])
        request.client = IPv4Address('TCP', '111.0.0.0', 2345)
        result = hook(request, 'hook_name')

        self.assertEqual(403, request.code)
        self.assertTrue(result.startswith('Error:001: '))

    def test_hook_no_header(self):
        """
        An error is raised when X-Github-Event header is not present.
        """
        result = hook(self.request, 'hook_name')

        self.assertTrue(result.startswith('Error:004: '))

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

    def test_hook_all_good_application_json(self):
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

    def test_hook_all_good_form_urlencoded(self):
        """
        x-www-form-urlencoded are parsed based on "payload" argument.
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
