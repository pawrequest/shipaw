from shipaw.config_loguru import get_loguru
from loguru import logger


def test_log():
    get_loguru()
    logger.info('This is a test log message')
