import docker
from log import logset,console

logger=logset('__init__')
logger.addHandler(console)
'''
import importlib
aa = importlib.import_module('lib.aa')
c = aa.c()
print(c)
'''

client = docker.from_env()

def clear_container(cname):
    try:
        ctn = client.containers.get(cname)
        ctn.stop()
        ctn.remove()
        logger.info('[+]%s\'s container %s removed'%(cname))  
    except:
        logger.warning('[*]container %s not found'%(cname))  
