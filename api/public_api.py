import copy

from lib.base_session import BaseSession
from lib.utils import get_jwt_token
from config.config import config
from config.public_api.endpoints import DEVICE_REGISTER, DEVICE_STATUS, DEVICE_UPDATE, DEVICE_GET_PIN


class PublicAPI:
    jwt_token = get_jwt_token()

    def __init__(self):
        self.s = BaseSession(host=config.hosts.PUBLIC_API_URL, is_https_secure=False)

    def _get_headers(self, authorization_header=None):
        headers = copy.deepcopy(self.s.default_headers)
        if authorization_header is not None:
            headers['Authorization'] = authorization_header
        return headers

    def register_device(self, devices, authorization_header=None):
        headers = self._get_headers()
        headers['Authorization'] = authorization_header if authorization_header else self.jwt_token
        payload = {"devices": devices}
        r = self.s.post(DEVICE_REGISTER, json=payload, headers=headers)
        return r

    def get_status_of_the_device(self, imei, authorization_header=None):
        headers = self._get_headers()
        headers['Authorization'] = authorization_header if authorization_header else self.jwt_token
        payload = {"devices": [{"imei": imei}]}
        r = self.s.post(DEVICE_STATUS, json=payload, headers=headers)
        return r

    def update_device(self, devices, authorization_header=None):
        headers = self._get_headers()
        headers['Authorization'] = authorization_header if authorization_header else self.jwt_token
        payload = {"devices": devices}
        r = self.s.post(DEVICE_UPDATE, json=payload, headers=headers)
        return r

    def get_pin(self, imei, challenge, authorization_header=None):
        headers = self._get_headers()
        headers['Authorization'] = authorization_header if authorization_header else self.jwt_token
        payload = {"imei": imei, "challenge": challenge}
        r = self.s.post(DEVICE_GET_PIN, json=payload, headers=headers)
        return r
