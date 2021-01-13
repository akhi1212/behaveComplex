import logging
import os

from config.config import config

logger = logging.getLogger(config.LOGGER_NAME)


def configure_logging(log_level, write_log_file='no'):
    if log_level:
        logger.setLevel(log_level.upper())
        formatter = logging.Formatter('[%(asctime)s] : %(name)s.%(lineno)d : %(levelname)s :   %(message)s')

        if write_log_file == 'yes':
            path = os.getcwd()
            log_file_path = os.path.join(path, 'TestAutomationAPI.log')

            fh = logging.FileHandler(log_file_path)
            fh.setLevel(log_level.upper())
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(log_level.upper())
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger
