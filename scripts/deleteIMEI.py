import re
import sys
from api.datastore_device_controller_api import DeviceControllerApi
from lib.utils import run_in_command_line
from config.config import config

host = 'ansible@bastion.qa.trustonic-alps.com'
table_prefix = 'alps-qa-svc-dynamodb-datastore'


def delete_imei(imei, print_output=False):
    if not imei:
        print('Please specify IMEI')
        return None
    print(f'Delete IMEI: {imei} \n')
    stdout, stderr = run_in_command_line(['ssh', host, f'./dynamodbDeleteImei.sh {imei} {table_prefix}'])
    if print_output:
        print(f'stdout: {stdout.decode("utf-8")}')
        print(f'stderr: {stderr.decode("utf-8")}')
    return stdout, stderr


def delete_all_test_imei(env_type='test4_qa'):
    config.re_init_for_env(env_type=env_type)
    ssh_tunnel = run_in_command_line(config.ssh_forw_cmd.split(), need_output=False)
    device_controller = DeviceControllerApi()
    test_imeis = []
    for tac in config.test_tacs.values():
        stream_filter = {"filters": [{"path": "tacData.tac", "value": tac}], "owner": config.owner}
        device_records_for_tac_str = device_controller.get_stream_device_records(filter_param=stream_filter).text
        match = re.findall(r'core":{"imei":"(.*?)"', device_records_for_tac_str)
        test_imeis += match
    total_num = len(test_imeis)
    print(f'Total number of IMEIs: {total_num}')
    try:
        for i in range(total_num):
            print(f'Deleting {i+1} of {total_num} \n')
            delete_imei(test_imeis[i])
    except Exception as error:
        print(f'Error: {str(error)}')
    finally:
        ssh_tunnel.kill()


if __name__ == '__main__':
    delete_imei(sys.argv[1] if len(sys.argv) > 1 else None, print_output=True)
