import datetime
import json
import unittest

import requests
import six

from augurycli.api import APIClient

from . import fake_api

try:
    from unittest import mock
except ImportError:
    import mock

from augurycli.api.constants import DEFAULT_TIMEOUT_SECONDS

def response(status_code=200, content='', headers=None, reason=None, elapsed=0,
             request=None, raw=None):
    res = requests.Response()
    res.status_code = status_code
    if not isinstance(content, six.binary_type):
        content = json.dumps(content).encode('ascii')
    res._content = content
    res.headers = requests.structures.CaseInsensitiveDict(headers or {})
    res.reason = reason
    res.elapsed = datetime.timedelta(elapsed)
    res.request = request
    res.raw = raw
    return res


def fake_resp(method, url, *args, **kwargs):
    key = None
    if url in fake_api.fake_responses:
        key = url
    elif (url, method) in fake_api.fake_responses:
        key = (url, method)
    if not key:
        raise Exception('{0} {1}'.format(method, url))
    status_code, content = fake_api.fake_responses[key]()
    return response(status_code=status_code, content=content)


fake_request = mock.Mock(side_effect=fake_resp)


def fake_get(self, url, *args, **kwargs):
    return fake_request('GET', url, *args, **kwargs)


def fake_post(self, url, *args, **kwargs):
    return fake_request('POST', url, *args, **kwargs)


def fake_put(self, url, *args, **kwargs):
    return fake_request('PUT', url, *args, **kwargs)


def fake_delete(self, url, *args, **kwargs):
    return fake_request('DELETE', url, *args, **kwargs)


url_base = '{0}/'.format(fake_api.prefix)


class BaseAPIClientTest(unittest.TestCase):
    def setUp(self):
        self.patcher = mock.patch.multiple(
            'augurycli.api.client.APIClient',
            get=fake_get,
            post=fake_post,
            put=fake_put,
            delete=fake_delete,
        )
        self.patcher.start()
        self.client = APIClient(base_url=url_base)
        # Force-clear authconfig to avoid tampering with the tests
        self.client._cfg = {'Configs': {}}

    def tearDown(self):
        self.client.close()
        self.patcher.stop()


class ApiTest(BaseAPIClientTest):
    def test_url_valid_resource(self):
        url = self.client._url('/hello/{0}/world', 'somename')
        self.assertEqual(url, '{0}{1}'.format(url_base, 'hello/somename/world'))

        url = self.client._url(
            '/hello/{0}/world/{1}', 'somename', 'someothername'
        )
        self.assertEqual(url, '{0}{1}'.format(
            url_base, 'hello/somename/world/someothername'
        ))

        url = self.client._url('/hello/{0}/world', 'some?name')
        self.assertEqual(url, '{0}{1}'.format(url_base, 'hello/some?name/world'))

        url = self.client._url("/images/{0}/push", "localhost:5000/image")
        self.assertEqual(url, '{0}{1}'.format(
            url_base, 'images/localhost:5000/image/push'
        ))

    def test_url_invalid_resource(self):
        self.assertRaises(ValueError, self.client._url, '/hello/{0}/world', ['sakuya', 'izayoi'])

    def test_url_no_resource(self):
        url = self.client._url('/simple')
        self.assertEqual(url, '{0}{1}'.format(url_base, 'simple'))

    def test_url_including_path(self):
        base = url_base + 'api/'
        self.client.base_url = base
        url = self.client._url('/simple')
        self.assertEqual(url, '{0}{1}'.format(base, 'simple'))

    def test_auth_header(self):
        self.client.fetch_config()

        fake_request.assert_called_with(
            'GET',
            url_base + 'runner/config'
        )

    def test_kwargs(self):
        self.client.token = 'absc'
        resp = self.client._update_kwargs()

        self.assertEqual(resp['timeout'], DEFAULT_TIMEOUT_SECONDS)
        self.assertEqual(resp['auth'], 'absc')

    def test_kwargs_override(self):
        resp = self.client._update_kwargs(timeout=2)

        self.assertEqual(resp['timeout'], 2)

