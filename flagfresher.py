# -*- coding: utf-8 -*-
import random
from models import db,Teams,Flags,math,Round,containers
import time
import hashlib
from sqlalchemy import func
import datetime
import threading

timespan = 1 * 60


def make_flag_str(teamname):
    rnd = random.random()
    #print(teamname + str(rnd) + str(time.time()))
    token = hashlib.md5((teamname + str(rnd) + str(time.time())).encode()).hexdigest()
    return token

def errorfresh(x,flag):
    while True:
        x.freshflag(flag)
        time.sleep(30)


def countscore(r,mathobj,checkscore,attckscore):

    print('统计 %d 轮分数'%r)
    #统计check
    teams = Teams.query.all()
    checked = Round.query.join(containers,containers.id==Round.containerid).filter(Round.rounds==r).all()

    print checked

    #for i in mathobj:








    #统计丢分

    return




def init_team_flag(mathobj):
    global timespan
    themath = math.query.first()

    #匹配比赛信息，控制刷新时间在比赛进行时
    if themath:
        timespan = themath.flagflash * 60
        if (datetime.datetime.now()-themath.endtime).total_seconds() > 0 or (datetime.datetime.now()-themath.starttime).total_seconds() < 0 :
            print('=== Time up ===')
            print('[+]starttime',themath.starttime)
            print('[+]the time',datetime.datetime.now())
            print('[+]endtime',themath.endtime)
            print((datetime.datetime.now()-themath.endtime).total_seconds())
            print((datetime.datetime.now()-themath.starttime).total_seconds())
            #return False

    else:
        print('=== No math infomation ===')
        #return False

    #global round_cont
    #round_cont+=1
    #获取当前最大的轮数
    round_cont = db.session.query(func.max(Flags.rounds)).scalar() #Round.query.fields(Round.rounds).first()

    if round_cont:
        round_cont=round_cont+1
    else:
        round_cont=1

    flag_list=[]
    for i in mathobj:
        text = '%s %s check False'%(i.teamname,i.db_containers.typename)

        #记录 check_rezult 状态
        if i.db_containers.check_stat == 1:
            # Round(attackteamid,rounds,containerid,text,score=0)
            db.session.add(Round(0,round_cont-1,i.id,text,themath.checkscore))
        #   db.session.commit()
        #初始化新的一轮 check_rezult
        i.db_containers.check_stat = 0

        flag = Flags(i.id,make_flag_str(i.container_name),round_cont)
        
        flag_list.append(flag)
        try:  
            i.freshflag(flag.flag)
        except:
            i.db_containers.check_stat = 1
            print('Round %d flag fresh %s error'%(round_cont,i.teamname))
            t = threading.Thread(target=errorfresh,args=(i,flag.flag,))
            t.setDaemon(True)            
            t.start()
    db.session.add_all(flag_list)
    db.session.commit()


    countscore(round_cont-1,mathobj,themath.checkscore,themath.atacckscore)

    time.sleep(timespan)
    return round_cont



def main(r=0):
    return

    
if __name__ == "__main__":
    #global round_cont
    main()