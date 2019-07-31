import random
from models import db,Teams
import time
import hashlib
import threading
import base64
from dockercontr import yunnansimple_run
from log import logger

def start_docker(team):
    www_pass = make_token_str(team.teamcontainer)
    ssh_port = 30022 + (team.id * 100)
    www_port = 30080 + (team.id * 100)
    ports={'22/tcp':ssh_port,'80/tcp':www_port}
    team.sshpassword = www_pass
    db.session.commit()
    yunnansimple_run(team.teamcontainer,www_pass,ports)
    logger.info('%s container started'%(team.teamcontainer))

def make_token_str(teamname):
    rnd = random.random()
    #print(teamname + str(rnd) + str(time.time()))
    token = base64.b64encode(hashlib.md5((teamname + str(rnd) + str(time.time())).encode()).hexdigest()[8:20].encode())
    return token

def init_team_token(teams):
    for i in teams:
        #print(i.name,i.token,make_token(i.teamcontainer))
        i.token = make_token_str(i.teamcontainer)
        db.session.commit()
        print(i.teamcontainer,i.token)


def main():
    teams = Teams.query.all()
    init_team_token(teams)    
    
def start_awd():
    teams = Teams.query.all()

    threadlist =[]

    for i in teams:
        t = threading.Thread(target = start_docker,args=(i,))
        #start_docker(i)
        print('Creating thread %s' % i.teamcontainer)
        t.setDaemon(True)
        threadlist.append(t)
        t.start()

    for i in threadlist:
        print('thread join')
        i.join()


if __name__ == "__main__":
    main()

