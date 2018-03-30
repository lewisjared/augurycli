import requests
import six
from six.moves.urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from augurycli.util import kwargs_from_env
from .constants import DEFAULT_TIMEOUT_SECONDS, DEFAULT_BASE_URL
from .runner import RunnerMixin


class APIClient(requests.Session,
                RunnerMixin):
    def __init__(self, base_url=DEFAULT_BASE_URL, token=None, timeout=DEFAULT_TIMEOUT_SECONDS):
        super(APIClient, self).__init__()
        self.base_url = base_url
        self.timeout = timeout
        self.token = token

        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        self.mount('http://', HTTPAdapter(max_retries=retries))
        self.mount('https://', HTTPAdapter(max_retries=retries))

    def get(self, url, **kwargs):
        return super(APIClient, self).get(url, **self._update_kwargs(**kwargs))

    def put(self, url, **kwargs):
        return super(APIClient, self).put(url, **self._update_kwargs(**kwargs))

    def post(self, url, **kwargs):
        return super(APIClient, self).post(url, **self._update_kwargs(**kwargs))

    def delete(self, url, **kwargs):
        return super(APIClient, self).delete(url, **self._update_kwargs(**kwargs))

    def _update_kwargs(self, **kwargs):
        kwargs.setdefault('timeout', self.timeout)


        if self.token:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = 'Bearer ' + self.token

        return kwargs

    def _result(self, response, json=False, binary=False):
        assert not (json and binary)
        response.raise_for_status()

        if json:
            return response.json()
        if binary:
            return response.content
        return response.text

    def _url(self, path, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, six.string_types):
                raise ValueError(
                    'Expected a string but found {0} ({1}) '
                    'instead'.format(arg, type(arg))
                )
        return urljoin(self.base_url, urljoin('api/', path.format(*args, **kwargs).lstrip('/')))

    @classmethod
    def from_env(cls, **kwargs):
        timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT_SECONDS)
        return cls(timeout=timeout, **kwargs_from_env(**kwargs))
