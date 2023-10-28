import logging

LOGGER = logging.getLogger(__name__)

LOGGING_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGING_FORMAT = '[%(module)s] - %(asctime)s: %(message)s'
logging.basicConfig(level=logging.INFO,format=LOGGING_FORMAT,datefmt=LOGGING_DATE_FORMAT)