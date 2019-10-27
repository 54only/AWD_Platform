import docker

# for import log
import sys
sys.path.append("..")
from log import logset,console
from models import db,containers
client = docker.from_env()

logger=logset('__init__')
logger.addHandler(console)


class subjectclass(object):
    #container_name=''
    #check_rezult = True
    def __init__(self, teamid,teamname, sshport,serviceport,teampass,score):
        self.serviceport=serviceport
        self.teamid=teamid
        self.sshport=sshport
        self.teamname=teamname
        self.score = score
        self.teampass=teampass
        self.check_stat=0
        self.db_containers = containers(self.name,self.container_name,teampass, self.sshaccount, serviceport,sshport,teamid,score)
        db.session.add(self.db_containers)
        db.session.commit()       
        self.id =  self.db_containers.id

    def update_score(self):
        Q = containers.query.filter(containers.id == self.db_containers.id).first()
        Q.score = self.db_containers.score
        db.session.commit()
        self.db_containers.score = Q.score

    def update_checkstat(self):
        Q = containers.query.filter(containers.id == self.db_containers.id).first()
        Q.check_stat = self.db_containers.check_stat
        db.session.commit()
        self.db_containers = Q

    def update_attackstat(self):
        Q = containers.query.filter(containers.id == self.db_containers.id).first()
        Q.attack_stat = self.db_containers.attack_stat
        db.session.commit()

    def create_containers(self):
        self.ctn = client.containers.create(self.image_name,
            #command=cmd,
            detach=True,
            ports = {'22/tcp':self.sshport,'80/tcp':self.serviceport} ,
            #volumes = {'/var/www/html/':{'bind':volpath,'mode':'rw'}},
            name = self.container_name,
            #environment = ["MYSQL_ROOT_PASSWORD=root"],
            #entrypoint = '/run.sh'
            )
        logger.info('[+]%s\'s container %s Created'%(self.teamname,self.container_name))

    def clear_container(self):
        try:
            self.ctn = client.containers.get(self.container_name)
            self.ctn.stop()
            self.ctn.remove()
            logger.info('[+]%s\'s container %s removed'%(self.container_name))  
        except:
            logger.warning('[*]container %s not found'%(self.container_name))  

    def start(self):
        self.ctn.start()
        logger.info('[+]%s\'s container %s started'%(self.teamname,self.container_name))  
    def stop(self):
        self.ctn.stop()
        logger.info('[+]%s\'s container %s stopped'%(self.teamname,self.container_name)) 


    def check_L1(self):
        self.update_checkstat()
        return self.db_containers.check_stat
    def check_L2(self):
        return self.db_containers.check_stat
    def check_L3(self):
        return self.db_containers.check_stat



    def freshflag(self,flag):
        self.ctn.exec_run('/bin/bash -c "echo %s > /flag"' % flag)
        logger.info('%s\' %s freshflag %s ok'%(self.teamname,self.name,flag))

    def run(self):
        self.ctn.start()






















