import copy

from lib.base_session import BaseSession
from config.config import config
from config.device_service_api.endpoints import DS_ENROL,DS_CHECKIN


class DeviceServiceApi:
    def __init__(self):
        self.s = BaseSession(host=config.hosts.DEVICE_SERVICE_URL, is_https_secure=False)

    def _get_headers(self):
        headers = copy.deepcopy(self.s.default_headers)
        return headers

    def post_enrol(self, enrol_json):
        headers = self._get_headers()
        r = self.s.post(DS_ENROL, json=enrol_json, headers=headers)
        return r

    def post_checkin(self, checkin_json, authorization_header):
        headers = self._get_headers()
        headers['Authorization'] = authorization_header
        r = self.s.post(DS_CHECKIN, json=checkin_json, headers=headers)
        return r
