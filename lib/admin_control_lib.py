import copy
import os

from api.datastore_admin_controller_api import AdminControllerApi
from resources.data_models import ADMIN_SAMPLE_JSON
from config.config import config
from datetime import datetime as dt


def setup_admin_record():
    """
    Setup admin record on server

    Will create admin record if not exist or update to default parameters

    :return: None
    """
    with open(os.path.dirname(__file__) + r'/../resources/policy_server_keys/policy_server_public.key', 'r') as pubKey:
        rsa_public_key = pubKey.read()
    key = rsa_public_key.replace("\n", "")

    record_admin = copy.deepcopy(ADMIN_SAMPLE_JSON)
    record_admin["id"] = record_admin["model"]["id"] = config.id_test_admin
    record_admin["model"]["publicKey"] = key
    if config.kg_server_url:
        record_admin['knoxGuardSettings']['server'] = config.kg_server_url
    update_admin_record(record_admin)
    ADMIN_SAMPLE_JSON.update(record_admin)


def update_admin_record(record=None, tac_entity=None, custom_properties=None, holidays=None):
    """
    Updates admin record on server via Datastore Controller

    :param record: data model with predefined parameters to update
    :param tac_entity: tac entity to add to admin record
    :param custom_properties: custom properties to add to admin record
    :param holidays: dictionary with predefined holidays
    :return: updated admin record
    """
    admin_api = AdminControllerApi()
    record_admin = record if record is not None else copy.deepcopy(admin_api.admin_model)
    if tac_entity:
        record_admin['model']['tacMap'].update(tac_entity)
    if custom_properties:
        record_admin['model']['customProperties'].update(custom_properties)
    if holidays:
        record_admin['model']['holidays'] = holidays
    r = admin_api.update_single_record(record_admin)
    r.raise_for_status()
    return record_admin


def generate_tac_entity(imei: str, provisioning='ALPS'):
    """
    Generates tac data model to be added into admin record

    :param imei: device`s imei; if None will take tac from config by provisioning else first 8 symbols from imei
    :param provisioning: provisioning type: "ALPS" or "KNOX_GUARD"
    :return: tac data model
    """
    tac = imei[:8] if imei else config.test_tacs[provisioning]
    tac_entity = {tac: {
                "tac": tac,
                "modelMarketingName": "AUTmodelMarketingName_" + tac,
                "modelFormalName": "AUTmodelFormalName_" + tac,
                "brandName": "AUTbrandName_" + tac,
                "provisioningType": provisioning,
                "ztemanufacturer": "null"

            }}
    return tac_entity


def generate_custom_properties_entity(custom_properties: dict):
    """
    Generates custom properties data model to be added into admin record

    :param custom_properties: custom properties dictionary {property_name: default_value}
    :return: custom properties data model
    """
    custom_properties_entity = {}
    for property_name, def_value in custom_properties.items():
        custom_properties_entity.update({property_name: {"defaultValue": def_value, "description": property_name,
                                                         "disabled": False}})
    return custom_properties_entity


def get_admin_holidays():
    """
        Returns list with days of month that are configured as holidays for admin account
    """
    holidays = []
    for holiday in get_admin_record()["model"]["holidays"]:
        if holiday["month"] == dt.now().month or holiday["month"] == (holiday["month"] + 1) % 12:
            holidays.append(holiday["dayOfMonth"])
    return holidays


def get_admin_record(admin_id: str = None):
    """
    Get single admin record

    :param admin_id: admin id, e.g. '/anyMNO/admin'
    :return: admin record
    """
    admin_api = AdminControllerApi()
    if not admin_id:
        admin_id = config.id_test_admin
    r = admin_api.get_records([admin_id])
    r.raise_for_status()
    r_data = r.json()
    assert r_data['records'], f"Admin record {admin_id} not found"
    return r_data['records'][0]
