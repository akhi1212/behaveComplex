import os

from configparser import ConfigParser

import env


def get_csv_download_dir(create_dir=True):
    download_dir = os.path.join(str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                os.path.join("resources", "download"))
    if create_dir:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
    return download_dir


def resolve_host_from_env(name):
    try:
        _host = os.environ[name]
    except KeyError:
        _host = None
    return _host


class Hosts:
    DATASTORE_URL = None
    PS_SERVER_URL = None
    ADMIN_FRONT_END_URL = None
    KC_REDIRECT_URI = None
    KC_AUTH_URL = None
    KC_TOKEN_URL = None
    GUI_FRONTEND = None
    DEVICE_SERVICE_URL = None
    PUBLIC_API_URL = None


class Config:
    parser = ConfigParser()
    environment = 'local'
    config_file = 'local_config'
    hosts = Hosts()

    def __init__(self, env_type='local'):
        self.environment = env_type
        self.config_file = env_type + '_config'

        config_path = os.path.dirname(__file__) + '/' + self.config_file
        self.parser.read(config_path)

        self.log_level = self.parser.get('Log', 'LOG_LEVEL', fallback='INFO')
        self.log_to_file = self.parser.get('Log', 'WRITE_TO_FILE', fallback='no')

        for host in dir(self.hosts):
            if not host.startswith('_'):
                if not resolve_host_from_env(host):
                    setattr(self.hosts, host, self.parser.get('Hosts', host))

        self.id_test_admin = self.parser.get('Test Data', 'ID_TEST_ADMIN', fallback='/anyMNO/admin')
        self.owner = self.parser.get('Test Data', 'OWNER', fallback='/anyMNO')
        self.ssh_forw_cmd = self.parser.get('Env', 'SSH_FORW_CMD', fallback=None)
        self.kg_server_url = self.parser.get('Env', 'KG_SERVER_URL', fallback=None)

        self.web_ui_wait_timeout = int(self.parser.get('WEB UI', 'WAIT_TIMEOUT', fallback=5))
        self.web_ui_headless = True if self.parser.get('WEB UI', 'HEADLESS', fallback='yes') == 'yes' else False

        self.real_device_imei = self.parser.get('Device Data', 'IMEI',
                                                fallback="Real device IMEI is not found. "
                                                         "Required for device check tes cases")

    def re_init_for_env(self, env_type='local'):
        self.__init__(env_type)


config = Config()

config.test_tacs = {'ALPS': '86405604', 'KNOX_GUARD': '35322811'}
config.SERIAL_TEST = "1234567890"

config.KC_CLIENT_ID = r'admin-service'
config.KC_CLIENT_SECRET = r'c1dc6e8e-98ef-422c-b549-783747803476'
config.KC_SCOPE = r'openid email profile'
config.KC_USER_ADVANCED = "test-advanced"
config.KC_USER_ADMIN = "test-admin"
config.KC_USER_BASIC = "test-basic"
config.KC_PASSWORD = "trustonic"
config.SCREENSHOT_PATH = os.path.join(env.PROJ_ROOT, "resources", "screenshots")
config.LOGGER_NAME = "AUTO_TESTS"

usernames = {
    "Read-Only User": config.KC_USER_BASIC,
    "Read-Write User": config.KC_USER_ADVANCED,
    "Admin User": config.KC_USER_ADMIN
}
