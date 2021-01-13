import copy
from dataclasses import asdict
from lib.base_session import BaseSession
from config.config import config
from config.datastore_provision_controller_api.endpoints import PROVISION_FETCH_URI
from config.datastore_provision_controller_api.provision_payloads import ProvisionRecord, FetchProvisionRecord


class ProvisionControllerApi:
    def __init__(self):
        self.s = BaseSession(host=config.hosts.DATASTORE_URL, is_https_secure=False)

    def _get_headers(self):
        headers = copy.deepcopy(self.s.default_headers)
        return headers

    def fetch_provision_records(self, imei, type):
        headers = self._get_headers()
        provision_payload = asdict(ProvisionRecord(imei, type))
        fetch_request_body = asdict(FetchProvisionRecord([provision_payload]))

        # Converts the object instance into dictionary to pass in as json payload
        fetch_record_response = self.s.post(PROVISION_FETCH_URI, json=fetch_request_body, headers=headers)
        return fetch_record_response
