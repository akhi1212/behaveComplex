import copy

from lib.base_session import BaseSession
from config.config import config
from config.admin_api.endpoints import ENROL_DEVICES_FILE
from lib.utils import get_admin_access_token


class DeviceRestController:
    def __init__(self):
        self.s = BaseSession(host=config.hosts.ADMIN_FRONT_END_URL, is_https_secure=False)
        self.jwt_token = get_admin_access_token()

    def _get_headers(self, authorization_header=None):
        headers = copy.deepcopy(self.s.default_headers)
        if authorization_header is not None:
            headers['Authorization'] = authorization_header
        return headers

    def device_enrolment(self, file_path, authorization_header=None):
        headers = self._get_headers()
        headers['Authorization'] = authorization_header if authorization_header else self.jwt_token
        del headers['Content-Type']
        files = {'file': open(file_path, 'rb')}
        r = self.s.post(ENROL_DEVICES_FILE, files=files, headers=headers)
        return r
