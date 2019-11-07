import docker

# for import log
import sys
sys.path.append("..")
from log import logset,console
from models import db,containers,Session

client = docker.from_env()

logger=logset('subject.__init__')
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
        
        self.session = Session()
        self.containers=containers
        self.db_containers = containers(self.name,self.container_name,self.teampass, self.sshaccount, self.serviceport,self.sshport,self.teamid,self.score)
        try:
            self.session.add(self.db_containers)
            self.session.commit()        
            self.id =  self.db_containers.id
        except:
            pass
        self.session.close()

    def update_score(self):
        self.session = Session()
        Q = self.containers.query.with_session(self.session).filter(containers.id == self.db_containers.id).first()
        Q.score = self.db_containers.score
        self.session.commit()
        self.session.close()
        #self.db_containers.score = Q.score
        print self.container_name,'update_score sucessed'
        return

    def update_checkstat(self):
        try:
            #print '__init__, update_checkstat',self.db_containers.id
            #db.session.commit()
            self.session = Session()
            Q = self.containers.query.with_session(self.session).filter(containers.id == self.db_containers.id).first()
            #if Q.check_stat != self.db_containers.check_stat or Q.attack_stat != self.db_containers.attack_stat:
            Q.check_stat = self.db_containers.check_stat
            #Q.attack_stat = self.db_containers.attack_stat
            self.session.commit()
            #self.db_containers = Q
            self.session.close()
            #self.db_containers = containers.query.filter(containers.id == self.db_containers.id).first()


        except Exception,e:
            print '[*]__init__, update_checkstat ERROR',self.container_name
            print e

    def update_attackstat(self):
        try:
            #db.session.commit()
            self.session = Session()
            Q = self.containers.query.with_session(self.session).filter(containers.id == self.db_containers.id).first()
            Q.attack_stat = self.db_containers.attack_stat
            self.session.commit()
            self.session.close()
        except Exception,e:
            print '[*]__init__, update_attackstat ERROR',self.container_name
            print e

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
        #self.update_checkstat()
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






















