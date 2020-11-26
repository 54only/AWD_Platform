# -*- coding: utf-8 -*-
from models import db,Teams,Scores,Round,Flags,User
import random
import base64
import hashlib
from log import logset
import time
#from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

logger = logset('init')

def make_token_str(teamname):
    rnd = random.random()
    s = (teamname + str(rnd) + str(time.time()))
    token = base64.b64encode(hashlib.md5(s.encode()).hexdigest()[8:20].encode())
    return token.decode()


def init_main(npcteams=3):
    userlist = []
    teamlist = []
    npcpassword = make_token_str('abc@123xxx')
    for i in open('users.txt').read().splitlines():
        if len(i)>10:
            team,username , userpass = i.split(' ')
            userlist.append([team,username,userpass])
            teamlist.append(team)

    for i in range(npcteams):
        team,username , userpass = 'NPC' + str(i),'NPC' + str(i),npcpassword
        userlist.append([team,username,userpass])
        teamlist.append(team)


    teamlist=list(set(teamlist))
    #print userlist
    #print teamlist,list(set(teamlist))
    
    for i in teamlist:
        db.session.add(Teams(i ,'', make_token_str(i), make_token_str(i))) #name,country,token,sshpassword
    db.session.commit()

    teams = Teams.query.all()
    teamdic={}
    for i in teams:
        teamdic[i.name]=i.id
    #print teamdic
    print ('TeamId\tTeamName\tUserName\tUserPassword')
    for i in userlist:
        team,username,userpass = i
        teamid = teamdic[team]

        print ('%d\t%s\t%s\t%s'%(teamid,team,username,userpass ))
        db.session.add(User(username,userpass,teamid))
    db.session.commit()

if __name__ == "__main__":
    init_main()