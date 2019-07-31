# -*- coding: utf-8 -*-
import random
from models import db,Teams,Flags,Round
import time
import hashlib
import base64
from sqlalchemy import func
from checker import service_checker
from dockercontr import freshflag2


timespan = 1 * 60
round_cont = 0
round_max = 1200
score_unit = 200
service_down = 200
score_start = 100000


def make_flag_str(teamname):
    rnd = random.random()
    #print(teamname + str(rnd) + str(time.time()))
    token = hashlib.md5((teamname + str(rnd) + str(time.time())).encode()).hexdigest()
    return token

#@asyncio.coroutine
def count_score(round_cont):
    #lost_score = Round.query(Round.defenseteamid,counta(Round.defenseteamid)).filter(Round.rounds==round_cont,Round.attackteamid!=0).group_by(Round.defenseteamid).all()
    lost_score = db.session.query(Round.defenseteamid,func.count(Round.defenseteamid)).filter(Round.rounds==round_cont,Round.attackteamid!=0).group_by(Round.defenseteamid).all()
    print(lost_score)
    #lost_score = db.session.query(Round.defenseteamid,func.count(Round.defenseteamid)).group_by(Round.defenseteamid).all()
    
    
    for i in lost_score:
        scroe_avg = score_unit // i[1]
        #print(scroe_avg)
        print('lost team id',i[0],'lost times',i[1],'avg_score',scroe_avg)
        db.session.query(Round).filter(Round.defenseteamid ==i[0],Round.rounds==round_cont,Round.attackteamid!=0).update({"score":scroe_avg})
        db.session.commit()
    #print(lost_score)
    
    #print(1)
    check_score = db.session.query(Round.defenseteamid).filter(Round.rounds==round_cont,Round.attackteamid==0).group_by(Round.defenseteamid).all()
    print('=== start count service score ===')
    print(check_score)
    teams = Teams.query.all()
    print(teams)

    scroe_avg = ( service_down) // (len(teams)-len(check_score))
    service_down_team_list=[]
    for i in check_score:
        service_down_team_list.append(i[0])
    print(service_down_team_list)
    service_down_team=[]
    service_up_team=[]
    teamname={}
    for eteam in teams:
        if eteam.id in service_down_team_list:
            service_down_team.append(eteam.id)
        else:
            service_up_team.append(eteam.id)
        teamname[eteam.id]=eteam.name

    for i in service_down_team:
        for j in service_up_team:
            db.session.add(Round(j,i,round_cont,u"%s 躺赢获取 %s 的故障分"%(teamname[j],teamname[i]),scroe_avg))
    db.session.commit()

    

    print('count of service down teams',len(check_score),service_down_team)
    print('count of service ok teams',len(teams)-len(check_score),service_up_team)
    print('=== end count service score ===')



def init_team_flag(teams):
    global round_cont
    round_cont+=1
    flag_list=[]
    for i in teams:
        flag = Flags(i.id,make_flag_str(i.teamcontainer),round_cont)
        flag_list.append(flag)
        print(i.teamcontainer,i.token,flag.flag)            
        print(service_checker(i.id,round_cont-1))
        try:  
            freshflag2(i.teamcontainer,flag.flag)
        except Exception as e:
            print('Round %d flag fresh error'%round_cont,e)
    count_score(round_cont-1)
    db.session.add_all(flag_list)
    db.session.commit()
    print('Round {} updated.'.format(round_cont))    


def main(r=0):
    global round_cont
    round_cont = r
    
    while round_cont < round_max+1:
        teams = Teams.query.all()
        init_team_flag(teams)
        time.sleep(timespan)

    
if __name__ == "__main__":
    #global round_cont
    main()