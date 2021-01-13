import copy

from lib.base_session import BaseSession
from config.config import config
from config.datastore_policy_controller_api.endpoints import POST_POLICY_RECORD_SINGLE, GET_POLICY_RECORD
from resources.data_models import POLICY_SAMPLE_JSON


class PolicyControllerApi:
    def __init__(self):
        self.s = BaseSession(host=config.hosts.DATASTORE_URL, is_https_secure=False)
        self.policy_model = POLICY_SAMPLE_JSON

    def _get_headers(self):
        headers = copy.deepcopy(self.s.default_headers)
        return headers

    def update_single_record(self, record):
        headers = self._get_headers()
        r = self.s.post(POST_POLICY_RECORD_SINGLE, json=record, headers=headers)
        if r.status_code == 200:
            self.policy_model = record
        return r

    def get_single_record(self, policy_id):
        headers = self._get_headers()
        r = self.s.post(GET_POLICY_RECORD, json={'ids': [policy_id]}, headers=headers)
        return r
