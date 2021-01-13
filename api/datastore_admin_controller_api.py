import copy

from lib.base_session import BaseSession
from config.config import config
from config.datastore_admin_controller_api.endpoints import POST_ADMIN_RECORD_SINGLE, POST_ADMIN_FETCH_RECORDS
from resources.data_models import ADMIN_SAMPLE_JSON


class AdminControllerApi:
    def __init__(self):
        self.s = BaseSession(host=config.hosts.DATASTORE_URL, is_https_secure=False)
        self.admin_model = ADMIN_SAMPLE_JSON

    def _get_headers(self):
        headers = copy.deepcopy(self.s.default_headers)
        return headers

    def update_single_record(self, record):
        headers = self._get_headers()
        r = self.s.post(POST_ADMIN_RECORD_SINGLE, json=record, headers=headers)
        if r.status_code == 200:
            self.admin_model = record
        return r

    def get_records(self, ids):
        headers = self._get_headers()
        r = self.s.post(POST_ADMIN_FETCH_RECORDS, json={'ids': ids}, headers=headers)
        return r
