# -*- coding: utf-8 -*-
from models import db,Teams,Flags,Round
import time
import requests
from log import logger
#from flagfresher import service_down


checktimespan=30
service_down = -200

def service_checker(teamid,rounds):
    port = 30080 + teamid*100
    url = 'http://127.0.0.1:%d/'%port
    check_rezult = True
    try:
        r =  requests.get(url)
        
        if b'Home' not in r.content:
            check_rezult = False 
            logger.info('team %d check index.php False' % teamid)

        url = 'http://127.0.0.1:%d/login.php'%port
        r =  requests.get(url)

        if r.status_code != 200 :
            check_rezult = False
            logger.info('team %d check login.php False' % teamid)
    except:
        check_rezult = False 
        logger.info('team %d check webservice False' % teamid)

    if rounds == 0 :
        return 'round 0 not check'
    
    
    '''
    check_rezult = True
    if teamid == 3:
        check_rezult = False
    if rounds > 5 and teamid == 2:
        check_rezult = False
    '''

    if check_rezult==False:
        if Round.query.filter(Round.attackteamid == 0,Round.defenseteamid ==teamid,Round.rounds==rounds).first():
            return 'team %d already checke false' % teamid
        else:
            team = Teams.query.filter(Teams.id==1).first()
            db.session.add(Round(0,teamid,rounds,'{} check False'.format(team.name.encode('utf-8')),service_down))
            #Round(j,i,round_cont,'%s 躺赢获取 %s 的故障分'%(teamname[j],teamname[i]),scroe_avg))
            db.session.commit()
        #db.session.query(Round).filter(Round.defenseteamid ==i[0],Round.rounds==rounds).update({"score":scroe_avg})
        return 'team %d check false' % teamid
    return 'team %d check ok' % teamid


def main():
    teams = Teams.query.all()
    #lastround = Flags.query.order_by(Flags.rounds.desc()).first() #.rounds

    while True:
        lastround = Flags.query.order_by(Flags.rounds.desc()).first() #.rounds
        if lastround:
            lastround=lastround.rounds
            for i in teams:
                print(service_checker(i.id,lastround))
        break
        time.sleep(checktimespan)

        #break



if __name__ == '__main__':
    main()