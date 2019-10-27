#-*- coding:utf-8 -*-
from __init__ import subjectclass,client
import time
import requests
# for import log
import sys
sys.path.append("..")
from log import logset,console
from models import db,containers
logger=logset('yunnam_simple')
logger.addHandler(console)


class o(subjectclass):
    #image_name = 'awd/yunnam_simple'
    image_name = '54only/yunnan_simple'
    name = 'yunnan_simple'
    #subjectclass.name = name
    sshaccount='www-data'



    def __init__(self, teamid,teamname, sshport,serviceport,teampass,score):
        self.container_name=self.name + '_' + str(teamid)
        super(o,self).__init__(teamid,teamname, sshport,serviceport,teampass,score)
        #subjectclass.container_name = self.container_name



    def create_containers(self):
        self.ctn = client.containers.create(self.image_name,
            #command=cmd,
            detach=True,
            ports = {'22/tcp':self.sshport,'80/tcp':self.serviceport} ,
            #volumes = {'/var/www/html/':{'bind':volpath,'mode':'rw'}},
            name = self.container_name,
            environment = ["MYSQL_ROOT_PASSWORD=root"],
            #entrypoint = '/run.sh'
            )
        logger.info('[+]%s\'s container %s Created'%(self.teamname,self.container_name))

    
    ##########################################################
    #
    # yunnansimple_run(name,www_pass,ports={'22/tcp':9922})
    # yunnansimple_run('team1','aaaaaaaa',ports={'22/tcp':20022,'80/tcp':20080})
    #
    ##########################################################

    def check_L1(self):

        if self.db_containers.check_stat >0:
            self.update_checkstat()
            return self.db_containers.check_stat

        try:
            url = 'http://127.0.0.1:%d/'%self.serviceport
            print url
            r =  requests.get(url,timeout=3)            
            if b'Home' not in r.content:
                self.db_containers.check_stat = 1 
                logger.info('[*]Check %s index.php False' % self.teamname)
                self.update_checkstat()
                return self.db_containers.check_stat
            

            url = 'http://127.0.0.1:%d/login.php'%self.serviceport
            r =  requests.get(url,timeout=3)

            if r.status_code != 200 :
                self.db_containers.check_stat = 1
                logger.info('[*]Check %s login.php False' % self.teamname)
                self.update_checkstat()
                return self.db_containers.check_stat
        except Exception,e :
            print e
            print self.db_containers.check_stat
            self.db_containers.check_stat = 1 
            logger.info('[*]Check %s webservice False:%s ' % (self.teamname,url))
            self.update_checkstat()
            return self.db_containers.check_stat




    def start(self):
        self.ctn.start()
        self.ctn.exec_run('service apache2 start')
        self.ctn.exec_run('service ssh start')
        logger.info('[+]%s\'s container %s started'%(self.teamname,self.container_name))  

    def run(self):
        name = self.container_name

        c=self.ctn

        # here timeout
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


        c.exec_run('/bin/sh -c "echo %s:%s | chpasswd"'%(self.sshaccount,self.teampass))

        msg = '/bin/sh -c "echo %s:%s | chpasswd"'%(self.sshaccount,self.teampass)
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

            statuscode,output = c.exec_run('/bin/sh -c "mysql -uroot -proot < /var/www/html/test.sql"')
            statuscode2,output2 = c.exec_run('/bin/sh -c "mysql -uroot -proot2 < /var/www/html/test.sql"')

            if b'denied' in output:
                msg = 'source database password wrong'
                logger.info("%s %s"%(name,msg)) 
                break
            elif b'denied' in output2:
                msg = 'Database Password is ok!'
                logger.info("%s %s"%(name,msg)) 
                break            
            else:
                msg = 'source database false , sleep 10 seconds'
                logger.warning("%s %s"%(name,msg))
                logger.warning("%s %s"%(name,output))
                logger.warning("%s %s"%(name,output2))
        msg="container is ready"   
        logger.info("%s %s"%(name,msg)) 
        return True
                       

        logger.info('%s container start ok'%name)