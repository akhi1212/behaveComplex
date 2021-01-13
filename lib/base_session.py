import logging
import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin

from config.config import config


default_headers = {"Content-Type": 'application/json'}


class BaseSession(object):
    def __init__(self, host, is_https_secure):
        self.logger = logging.getLogger(config.LOGGER_NAME + f".{self.__class__.__name__}")
        self.host = host
        self.is_HTTPS_secure = is_https_secure
        self._s = requests.Session()
        self.default_headers = default_headers
        if not self.is_HTTPS_secure:
            disable_warnings(InsecureRequestWarning)

    def form_request(self, url, kwa):
        _url = urljoin(self.host, url)
        return _url, kwa

    def get(self, url, **kwargs):
        self.logger.debug(f'GET url: {url}')

        _url, _kwargs = self.form_request(url, kwargs)
        result = self._s.get(_url, verify=self.is_HTTPS_secure, **_kwargs)

        self.logger.debug(f'GET Result: {result.status_code} {result.text}')
        return result

    def post(self, url, data=None, json=None, **kwargs):
        self.logger.debug(f'POST url: {url} data: {data} json: {json}')

        _url, _kwargs = self.form_request(url, kwargs)
        result = self._s.post(_url, data, json, verify=self.is_HTTPS_secure, **_kwargs)

        self.logger.debug(f'POST Result: {result.status_code} {result.text}')
        return result

    def put(self, url, data=None, json=None, **kwargs):
        self.logger.debug(f'PUT url: {url} data: {data} json: {json}')

        _url, _kwargs = self.form_request(url, kwargs)
        _kwargs['json'] = json
        result = self._s.put(_url, data, verify=self.is_HTTPS_secure, **_kwargs)

        self.logger.debug(f'PUT Result: {result.status_code} {result.text}')
        return result

    def delete(self, url, **kwargs):
        self.logger.debug(f'DELETE url: {url}')

        _url, _kwargs = self.form_request(url, kwargs)
        result = self._s.delete(_url, verify=self.is_HTTPS_secure, **_kwargs)

        self.logger.debug(f'DELETE Result: {result.status_code} {result.text}')
        return result

    def patch(self, url, data=None, json=None, **kwargs):
        self.logger.debug(f'PATCH url: {url} data: {data} json: {json}')

        _url, _kwargs = self.form_request(url, kwargs)
        result = self._s.patch(url=_url, data=data, json=json, verify=self.is_HTTPS_secure, **_kwargs)

        self.logger.debug(f'PATCH Result: {result.status_code} {result.text}')
        return result
