import logging


logging.basicConfig(level = logging.WARNING,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='log.txt')
logger = logging.getLogger(__name__)