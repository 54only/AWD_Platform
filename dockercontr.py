import docker
import os
import logging
import time
from log import logger

#logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='log.txt')
#logger = logging.getLogger(__name__)


client = docker.from_env()


def create_containers(image_name,cmd,volpath,ports={'22/tcp':9922},tag=''):
    ctn = client.containers.create(image_name,
        command=cmd,
        detach=True,
        ports = ports ,
        #volumes = {'/var/www/html/':{'bind':volpath,'mode':'rw'}},
        name = tag,
        environment = ["MYSQL_ROOT_PASSWORD=root"],
        #entrypoint = '/run.sh'
        )
    logger.info('%s created'%(tag))
    return ctn


def clear_container(name):
    # docker container prune
    # docker volume rm $(docker volume ls -qf dangling=true)
    
    try:
        ctn = client.containers.get(name)
        ctn.stop()
        ctn.remove()
        logger.info('container %s cleared'%(name))  
    except:
        logger.warning('container %s not found'%(name))  



def freshflag(container,flag):

    container.exec_run('/bin/bash -c "echo %s > /flag"' % flag)
    logger.info('%s freshflag %s ok'%(container_id,flag))


def freshflag2(container_id,flag):
#test = client.containers.run('ubuntu:18.10',['service apache2 start','/bin/bash'],detach=True)
    container = client.containers.get(container_id)
    container.exec_run('/bin/bash -c "echo %s > /flag"' % flag)
    logger.info('%s freshflag %s ok'%(container_id,flag))

#freshflag('awesome_blackwell','helloworld')


##########################################################
#
# yunnansimple_run(name,www_pass,ports={'22/tcp':9922})
# yunnansimple_run('team1','aaaaaaaa',ports={'22/tcp':20022,'80/tcp':20080})
#
##########################################################
def yunnansimple_run(name,www_pass,ports={'22/tcp':9922}):
    clear_container(name)
    #image_name = 'awd/yunnam_simple'
    image_name = '54only/yunnan_simple'
    cmd=''
    volpath=''
    
    try:
        client.images.get(image_name)
    except:
        print('[+]Pulling docker image ,please wait a few minutes')
        logger.info('[+]Pulling docker image ,please wait a few minutes')
        client.images.pull(image_name)
    
    
    
    c = create_containers(image_name,cmd,volpath,ports=ports,tag=name)

    c.start()  

    while True:
        time.sleep(10)  
        if b'MySQL init process done. Ready for start up.' in c.logs():
            if b'/var/run/mysqld/mysqld.sock' in c.logs():
                msg = 'mysql init ok'
                logger.info("%s %s"%(name,msg)) 
                break
        msg = 'mysql initing ...'
        logger.warning("%s %s"%(name,msg)) 


    c.exec_run('/bin/sh -c "echo www-data:%s | chpasswd"'%www_pass.decode())

    msg = '/bin/sh -c "echo www-data:%s | chpasswd"'%www_pass.decode()
    logger.info("%s %s"%(name,msg)) 
    c.exec_run('chown www-data:www-data /var/www/html -R')
    msg = 'chown /var/www/html ok'     
    logger.info("%s %s"%(name,msg)) 
    c.exec_run('service ssh start')
    msg =  'ssh ok'   
    logger.info("%s %s"%(name,msg)) 
    c.exec_run('service apache2 start')
    msg = 'apache2 ok'   
    logger.info("%s %s"%(name,msg)) 
    

    while True:
        time.sleep(2) 
        if b'denied' in c.exec_run('/bin/sh -c "mysql -uroot -proot < /var/www/html/test.sql"'):
            msg = 'source database password wrong'
            logger.info("%s %s"%(name,msg)) 
            break
        elif b'denied' in c.exec_run('/bin/sh -c "mysql -uroot -proot2 < /var/www/html/test.sql"'):
            msg = 'Database Password is ok!'
            logger.info("%s %s"%(name,msg)) 
            break            
        else:
            msg = 'source database false , sleep 10 seconds'
            logger.warning("%s %s"%(name,msg))
    msg="container is ready"   
    logger.info("%s %s"%(name,msg)) 
    return True
                   

    logger.info('%s container start ok'%name)
