import copy

from lib.base_session import BaseSession
from config.config import config
from config.datastore_device_controller_api.endpoints import GET_DEVICE_RECORD, GET_STREAM_DEVICE_RECORDS
from resources.data_models import DEVICE_SAMPLE_JSON


class DeviceControllerApi:
    def __init__(self):
        self.s = BaseSession(host=config.hosts.DATASTORE_URL, is_https_secure=False)
        self.device_model = DEVICE_SAMPLE_JSON

    def _get_headers(self):
        headers = copy.deepcopy(self.s.default_headers)
        return headers

    def get_device_record(self, imei):
        headers = self._get_headers()
        r = self.s.get(GET_DEVICE_RECORD.format(imei=imei), headers=headers)
        return r

    def get_stream_device_records(self, filter_param):
        headers = self._get_headers()
        r = self.s.post(GET_STREAM_DEVICE_RECORDS, json=filter_param, headers=headers)
        return r
