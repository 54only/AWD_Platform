#-*- coding:utf-8 -*-
from __init__ import subjectclass,client



# for import log
import sys
sys.path.append("..")
from log import logset,console
#from models import db,containers
logger=logset('subject.pwn_simple')
logger.addHandler(console)


class o(subjectclass):
    image_name = '54only/pwntest'
    name = 'pwn_simple'
    sshaccount='ctf'
    def __init__(self, teamid,teamname, sshport,serviceport,teampass,score):
        self.container_name=self.name + '_' + str(teamid)
        super(o,self).__init__(teamid,teamname, sshport,serviceport,teampass,score)
        #subjectclass.container_name = self.container_name
        #db.session.add(containers(self.container_name,teampass, self.sshaccount, serviceport,sshport,teamid,score))
        #db.session.commit()

    def create_containers(self):
        self.ctn = client.containers.create(self.image_name,
            #command=cmd,
            detach=True,
            ports = {'22/tcp':self.sshport,'9999/tcp':self.serviceport} ,
            #volumes = {'/var/www/html/':{'bind':volpath,'mode':'rw'}},
            name = self.container_name,
            #environment = ["MYSQL_ROOT_PASSWORD=root"],
            entrypoint = '/start.sh'
            )
        logger.info('[+]%s\'s container %s Created'%(self.teamname,self.container_name))



    def freshflag(self,flag):
        self.ctn.exec_run('/bin/bash -c "echo %s > /home/ctf/flag"' % flag)
        logger.info('%s %s freshflag %s ok'%(self.teamname,self.name,flag))


    def start(self):
        self.ctn.start()
        self.ctn.exec_run('service ssh start')
        logger.info('[+]%s container %s started'%(self.teamname,self.container_name)) 

    def run(self):
        self.ctn.start()
        self.ctn.exec_run('/bin/sh -c "echo ctf:%s | chpasswd"'%self.teampass)
        self.ctn.exec_run('service ssh start')
        self.ctn.exec_run('chown ctf:ctf /home/ctf/pwn')
        logger.info('%s container %s start ok'%(self.name,self.container_name))

    def check_L1(self):
        #self.update_checkstat()

        try:
            statuscode,output = self.ctn.exec_run('/bin/sh -c "ls -l | grep pwn"')
        except:
            self.ctn = client.containers.get(self.container_name)
            statuscode,output = (0,'restarting...')#self.ctn.exec_run('/bin/sh -c "ls -l | grep pwn"')
        
        if '7200' in output:
            return True
        else:
            logger.info('[*]Check %s False' % self.teamname)
            self.db_containers.check_stat = 1 
            self.update_checkstat()
            return False
        return self.db_containers.check_stat
