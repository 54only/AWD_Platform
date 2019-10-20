import logging


logging.basicConfig(level = logging.WARNING,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='log.txt')
logger = logging.getLogger(__name__)

#logging.basicConfig(level = logging.WARNING,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='web_log.txt')
#logger_web = logging.getLogger(__name__)

