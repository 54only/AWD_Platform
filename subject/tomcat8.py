#-*- coding:utf-8 -*-
from __init__ import subjectclass,client

'''
source /etc/profile &&
source /etc/environment &&

sudo -H -u ctf /bin/bash -c '/usr/local/tomcat8.5.47/bin/catalina.sh start' &
'''
import sys
sys.path.append("..")
from log import logset,console
#from models import db,containers
logger=logset('subject.tomcat8')
logger.addHandler(console)


class o(subjectclass):
    image_name = '54only/tomcat8'
    name = 'tomcat8'
    sshaccount='ctf'
    def __init__(self, teamid,teamname, sshport,serviceport,teampass,score):
        self.container_name=self.name + '_' + str(teamid)
        super(o,self).__init__(teamid,teamname, sshport,serviceport,teampass,score)


    def create_containers(self):
        self.ctn = client.containers.create(self.image_name,
            #command=cmd,
            detach=True,
            ports = {'22/tcp':self.sshport,'8080/tcp':self.serviceport} ,
            #volumes = {'/var/www/html/':{'bind':volpath,'mode':'rw'}},
            name = self.container_name,
            environment = ["MYSQL_ROOT_PASSWORD=root"],
            entrypoint = '/run.sh'
            )
        logger.info('[+]%s\'s container %s Created'%(self.teamname,self.container_name))



    def start(self):
        self.ctn.start()
        self.ctn.exec_run("sudo -H -u ctf /bin/bash -c 'source /etc/profile;/usr/local/tomcat8.5.47/bin/catalina.sh start'")
        logger.info('[+]%s container %s started'%(self.teamname,self.container_name))         
        
    def run(self):
        self.ctn.start()
        self.ctn.exec_run('/bin/sh -c "echo ctf:%s | chpasswd"'%self.teampass)
        self.ctn.exec_run('chown -R ctf:ctf /usr/local/tomcat8.5.47')        
        self.ctn.exec_run("sudo -H -u ctf /bin/bash -c 'source /etc/profile;/usr/local/tomcat8.5.47/bin/catalina.sh start'")
        logger.info('%s container %s run config ok'%(self.name,self.container_name))        
        
        
        
    def check_L1(self):           
        
        try:
            statuscode,output = self.ctn.exec_run('/bin/sh -c "ps -ef"')
        except Exception,e:
            print e
            self.ctn = client.containers.get(self.container_name)
            statuscode,output = (0,'restarting...')#self.ctn.exec_run('/bin/sh -c "ls -l | grep pwn"')
        
        if 'tomcat8.5.47' in output:
            logger.info('[*]Check %s ok' % self.teamname)
            return True
        else:
            #print output
            logger.info('[*]Check %s False' % self.teamname)
            self.db_containers.check_stat = 1 
            self.update_checkstat()
            return False
        return self.db_containers.check_stat        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        