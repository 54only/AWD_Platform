#-*- coding:utf-8 -*-
import batch
import flagfresher
import checker
import os
import time
import models
from log import logset,console
import importlib
import threading
from Queue import Queue


thrds = 8       # docker 同时操作线程

npcteams = 3    #额外的npc队伍



q = Queue() 

logger = logset('start')
logger.addHandler(console)


models.main(npcteams) #初始化数据库




'''
主要流程

先创建容器，然后启动容器，再关闭容器，等比赛开始时再启动容器
'''
# port 规则为 3 00 队伍id 22 服务端口
subject =   {
            #'yunnam_simple': {'sshport':30022,'serviceport':30080},
            'pwn_simple':   {'sshport':30032,'serviceport':30090}
            }

#清除 docker 残留数据
#docker volume rm $(docker volume ls -qf dangling=true)




def container_starter():
    while not q.empty():
        tmp = q.get()
        tmp.start()
        q.task_done() 
        logger.info('[+]%s container %s started started' % (tmp.teamname,tmp.container_name))


def containers_worker():
    while not q.empty():
        tmp = q.get()
        logger.info('[+]%s container %s starting' % (tmp.teamname,tmp.container_name))
        tmp.run()
        logger.info('[+]%s container %s started' % (tmp.teamname,tmp.container_name))
        tmp.stop()
        q.task_done() 
        logger.info('[+]%s container %s started task_done' % (tmp.teamname,tmp.container_name))


def flagfresher_worker(mathobj):
    while True:        
        i = flagfresher.init_team_flag(mathobj)
        logger.info('[+]Round %d flag freshed'%i)

def checker_worker(mathobj):
    while True:
        checker.service_checker(mathobj)



def main():
    teams = models.Teams.query.all()


    #   subject/dockers
    #   teamid,teamname, sshport,serviceport
    #   containers
    #   name,sshpassword, sshaccount, serviceport,sshport,teamid,score
    score = models.math.query.first().startscore
    mathobj = []

    for s in subject:
        m = importlib.import_module('subject.'+s)


        for i in teams:
            teamid = i.id
            teamname = i.name
            sshport = subject[s]['sshport'] + 100*teamid
            serviceport = subject[s]['serviceport'] + 100*teamid
            teampass = i.sshpassword
            

            mathobj.append(m.o(teamid,teamname, sshport,serviceport,teampass,score))
            #sshpassword = i.ssh

    for i in mathobj:
        #print i.teamid,i.name,i.container_name
        q.put(i)
        logger.info('[+]Clearing %s container %s' % (i.teamname,i.container_name))

        i.clear_container()
        i.create_containers()
        logger.info('[+]%s container %s created' % (i.teamname,i.container_name))



    logger.info('[+]Ready to start containers')



    # 开始准备 docker

    threads = [threading.Thread(target=containers_worker) for i in xrange(thrds)]
    map(lambda x:x.setDaemon(True),threads)
    map(lambda x:x.start(),threads)
    map(lambda x:x.join(),threads)
    q.join()  


    logger.info('[+]ALL containers are ready')


    for i in mathobj:
        #print i.teamid,i.name,i.container_name
        q.put(i)

    # 开始启动 docker

    threads = [threading.Thread(target=container_starter) for i in xrange(thrds)]
    map(lambda x:x.setDaemon(True),threads)
    map(lambda x:x.start(),threads)
    map(lambda x:x.join(),threads)
    q.join() 
    logger.info('[+]ALL containers are started')

    # 开始刷新 flag
    logger.info('[+]starting fresh flag')
    t = threading.Thread(target=flagfresher_worker,args=(mathobj,))
    t.setDaemon(True)
    t.start()


    # 启动 checker

    logger.info('[+]starting checker')
    t1 = threading.Thread(target=checker_worker,args=(mathobj,))
    t1.setDaemon(True)
    t1.start()

    # 阻塞主线程

    while True:
        time.sleep(60)


if __name__ == '__main__':
    main()