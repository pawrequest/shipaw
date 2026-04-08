from loguru import logger

from shipaw.config_loguru import get_loguru


def test_log():
    get_loguru()
    logger.info('This is a test log message')
