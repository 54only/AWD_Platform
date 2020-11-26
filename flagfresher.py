# -*- coding: utf-8 -*-
import random
from models import db,Teams,Flags,Round,containers,Scores
import time
import hashlib
from sqlalchemy import func
import datetime
import threading
import decimal
from log import logset,console


logger = logset('flagflasher')
logger.addHandler(console)



def make_flag_str(teamname):
    rnd = random.random()
    #print(teamname + str(rnd) + str(time.time()))
    token = hashlib.md5((teamname + str(rnd) + str(time.time())).encode()).hexdigest()
    return token

def errorfresh(x,flag):
    while True:
        try:
            x.freshflag(flag)
            logger.info('%s %sFlag freshed : %s'%(x.teamname,x.container_name,flag))
            return
        except:            
            logger.warning('%s %s Flag fresh error'%(x.teamname,x.container_name))
        time.sleep(30)


def countscore(r,mathobj,checkscore,attckscore):

    print('统计 %d 轮分数'%r)
    #统计check
    #队伍数量
    team_count = Teams.query.count()
    #被扣分的container.id和typename
    checked = Round.query.join(containers,containers.id==Round.containerid).filter(Round.rounds==r,Round.attackteamid==0).with_entities(containers.typename,containers.id).all()

    

    checked_score_sum={}

    for i in checked:
        if checked_score_sum.get(i[0]):
            checked_score_sum[i[0]]['score'] += checkscore
            checked_score_sum[i[0]]['containers'].append(i[1])
        else:
            checked_score_sum[i[0]]={}
            checked_score_sum[i[0]]['containers']=[]
            checked_score_sum[i[0]]['score'] = checkscore
            checked_score_sum[i[0]]['containers'].append(i[1])


    for i in checked_score_sum:
        if team_count > len(checked_score_sum[i]['containers']):
            checked_score_sum[i]['avgscore'] = checked_score_sum[i]['score'] / (team_count-len(checked_score_sum[i]['containers'])+0.0)
        else:
            checked_score_sum[i]['avgscore'] = 0


    print ('=============================')
    print ('check情况')
    print ('=============================')

    print (checked_score_sum)


    for i in mathobj:
        for c in checked_score_sum:
            if i.db_containers.typename == c:
                print (c,i.db_containers.id)
                #print i.teamid
                print (i.db_containers.score)
                if i.db_containers.id in checked_score_sum[c]['containers']:
                    i.db_containers.score -= decimal.Decimal(checkscore)
                else:
                    i.db_containers.score += decimal.Decimal(checked_score_sum[c]['avgscore']).quantize(decimal.Decimal('0.00'))
                print (i.db_containers.score)
                i.update_score()


    #统计丢分

    checked = Round.query.join(containers,containers.id==Round.containerid).filter(Round.rounds==r,Round.attackteamid!=0).with_entities(containers.typename,containers.id,Round.attackteamid).all()
    #print checked
    checked_score_sum={}

    for i in checked:
        #print 'Key ERROR?',i           
        
        if checked_score_sum.get(i[0]):
            if checked_score_sum[i[0]].get(i[1]):
                checked_score_sum[i[0]][i[1]]['attackteams'].append(i[2])
            else:
             
                checked_score_sum[i[0]][i[1]]={}
                checked_score_sum[i[0]][i[1]]['attackteams']=[]
                checked_score_sum[i[0]][i[1]]['attackteams'].append(i[2])
        else:
            checked_score_sum[i[0]]={}
            checked_score_sum[i[0]][i[1]]={}
            checked_score_sum[i[0]][i[1]]['attackteams']=[]
            checked_score_sum[i[0]][i[1]]['attackteams'].append(i[2])

    print ('=============================')
    print ('丢分情况')
    print ('=============================')

    for i in checked_score_sum:
        for j in checked_score_sum[i]:
            checked_score_sum[i][j]['avgscore'] = attckscore / (len(checked_score_sum[i][j]['attackteams'])+0.0)




    print ('=============================')
    print (checked_score_sum)
    print ('=============================')

    for i in checked_score_sum:
        for cid in checked_score_sum[i]:
            for x in Round.query.filter(Round.rounds==r,Round.containerid==cid).all():
                x.score = decimal.Decimal(checked_score_sum[i][cid]['avgscore'])
    db.session.commit()    


    for c in checked_score_sum:
        for i in mathobj:
            if i.db_containers.typename == c:
                for i1 in checked_score_sum[c]:
                    #print c,i.db_containers.id,i.db_containers.score
                    if i.db_containers.id == i1:
                        i.db_containers.score -= decimal.Decimal(attckscore)
                        #print c,i.db_containers.id,i.db_containers.score
                        #i.update_score()
                        #break
                    
                    if i.teamid in checked_score_sum[c][i1]['attackteams']:
                        i.db_containers.score += decimal.Decimal(checked_score_sum[c][i1]['avgscore']).quantize(decimal.Decimal('0.00'))
                        #print c,i.db_containers.id,i.db_containers.score
                        #i.update_score()
                        #continue
                        #break
            #i.session.commit()
            i.update_score()
             
    # 记录每轮的分数

    teams=Teams.query.all()

    for i in teams:
        #team_score = i.score() #r
        db.session.add(Scores(i.id,i.score(), r))
    db.session.commit()    
    return




def init_team_flag(mathobj,themath):
    #themath = models.math.query.first()
    #global round_cont
    #round_cont+=1
    #获取当前最大的轮数
    round_cont = db.session.query(func.max(Flags.rounds)).scalar() #Round.query.fields(Round.rounds).first()

    if round_cont:
        round_cont=round_cont+1
    else:
        round_cont=1

    #flag_list=[]
    for i in mathobj:
        text = '%s %s check False'%(i.teamname,i.db_containers.typename)

        #记录 check_rezult 状态
        if i.db_containers.check_stat == 1:
            # Round(attackteamid,rounds,containerid,text,score=0)
            db.session.add(Round(0,round_cont-1,i.id,text,-themath.checkscore))
        #   db.session.commit()
        #初始化新的一轮 check_rezult
        i.db_containers.check_stat = 0
        i.db_containers.attack_stat = 0
        i.update_checkstat()
        i.update_attackstat()
        #i.session.commit()
        flag = Flags(i.id,make_flag_str(i.container_name),round_cont)        
        #flag_list.append(flag)
        db.session.add(flag)
        db.session.commit()
        try:  
            i.freshflag(flag.flag)
            #logger.info('%s Flag fresed : %s'%(i.teamname,flag.flag))
        except:
            i.db_containers.check_stat = 1
            i.update_checkstat()
            #i.session.commit()
            logger.warning('Round %d flag fresh %s error'%(round_cont,i.teamname))
            t = threading.Thread(target=errorfresh,args=(i,flag.flag,))
            t.setDaemon(True)            
            t.start()
    #db.session.add_all(flag_list)
    #db.session.commit()


    countscore(round_cont-1,mathobj,themath.checkscore,themath.atacckscore)

    return round_cont



def main(r=0):
    return

    
if __name__ == "__main__":
    #global round_cont
    main()