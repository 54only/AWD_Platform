import logging




logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='log.txt')
logger = logging.getLogger(__name__)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.INFO)
#logging.basicConfig(level = logging.WARNING,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='web_log.txt')
#logger_web = logging.getLogger(__name__)

def logset(name):
    return logging.getLogger(name)