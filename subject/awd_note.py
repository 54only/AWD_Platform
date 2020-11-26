#-*- coding:utf-8 -*-
from .__init__ import subjectclass,client,docker
import os

# for import log
import sys
sys.path.append("..")
from log import logset,console
#from models import db,containers
logger=logset('subject.awd_note')
logger.addHandler(console)
imagename = 'awd_note'
#from models import db,Teams,containers

def build():
    try:
        img = client.images.get(imagename)
        logger.info('Image alread exists :'+imagename)
        return img
    except Exception as e:
        print(e)
        m100 = 1024*1024*1024
        logger.info('Image building :'+imagename)
        #print os.path.abspath('.')
        #return
        #,dockerfile='./pwn/awd_note/Dockerfile'
        client.images.build(path='./subject/source/pwn/awd_note',tag=imagename,container_limits={'memory':m100,'memswap':-1})
        return client.images.get(imagename)

class o(subjectclass):
    name = 'awd_note'
    sshaccount='pwn'
    def __init__(self, teamid,teamname, sshport,serviceport,teampass,score,ip,image):
        self.container_name=self.name + '_' + str(teamid)
        self.ip=ip
        self.image_name = image
        super(o,self).__init__(teamid,teamname, sshport,serviceport,teampass,score)

    def create_containers(self):
        path = (os.path.abspath('.'))
        #return
        pwn_path = '%s/run/team_%d/%s/bin/pwn'%(path,self.teamid,self.name)
        flag_path = '%s/run/team_%d/%s/flag'%(path,self.teamid,self.name)
        
        self.flag_path = flag_path

        client.api.create_container(self.image_name,
            #command='chown root:pwn /home/pwn/pwn',
            #mem_limit = '128m' ,
            detach=True,
            #ports = [self.sshport,self.serviceport ],
            #ports = {'22/tcp':self.sshport,'9999/tcp':self.serviceport} ,
            volumes = ['/home/pwn/flag','/home/pwn/pwn'],
            host_config =client.api.create_host_config(binds=[
                flag_path+':/home/pwn/flag:ro',
                pwn_path+':/home/pwn/pwn'
                ]
                ),
            # {'/home/pwn/':{'bind': '%s/run/team_%d/%s/bin/'%(path,self.teamid,self.name), 'mode': 'rw'},
            #             #'/home/pwn/flag':{'bind': '%s/run/team_%d/%s/flag'%(path,self.teamid,self.name), 'mode': 'ro'}
            #             },
            name = self.container_name,
            networking_config = client.api.create_networking_config({
                'awdnetwork': client.api.create_endpoint_config(
                    ipv4_address=self.ip,
                    #self='awdnetwork'
                    #aliases=['foo', 'bar'],
                    #links=['container2']
                )
            })
            )
        self.ctn = client.containers.get(self.container_name)
        #print (self.ctn.name)
        logger.info('[+]%s\'s container %s Created'%(self.teamname,self.container_name))


    def start(self):
        self.ctn.start()
        #self.ctn.exec_run('service ssh start')
        logger.info('[+]%s container %s started'%(self.teamname,self.container_name)) 

    def run(self):
        self.ctn.start()
        self.ctn.exec_run('/bin/sh -c "echo pwn:%s | chpasswd"'%self.teampass)
        #self.ctn.exec_run('service ssh start')
        #self.ctn.exec_run('chown ctf:ctf /home/ctf/pwn')
        logger.info('%s container %s start ok'%(self.name,self.container_name))

    def freshflag(self,flag):
        #self.ctn.exec_run('/bin/bash -c "echo %s > /home/ctf/flag"' % flag)
        open(self.flag_path,'wb').write(flag)
        logger.info('%s %s freshflag %s ok'%(self.teamname,self.name,flag))

# networking_config = docker_client.create_networking_config({
#     'network1': docker_client.create_endpoint_config(
#         ipv4_address='172.28.0.124',
#         aliases=['foo', 'bar'],
#         links=['container2']
#     )
# })

# ctnr = docker_client.create_container(
#     img, command, networking_config=networking_config
# )