# -*- coding: utf-8 -*-
from models import db,Teams,Scores,Round,Flags,User
import random
from log import logger
#from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

def init_main(teams = 10):
    


    for i in range(1,teams+1):
        country=token=name='NPC'+str(i)
        sshpassword='NULL'
        tmpteam=Teams(i,name,country,'team'+str(i),token,sshpassword)
        db.session.add(tmpteam)    
        db.session.commit()



    #Add administrator

    #adminuser=User(1,'admin','20be459727e35f01ad0e228a2aa9579d','NPC') #Admin@123!
    adminuser=User('admin','Admin@123!','NPC')
    db.session.add(adminuser)    
    db.session.commit()
    logger.info('awd database inited')
    print('Add administrator admin')

    #print(User.query.all())
    #print(Teams.query.all())



    try:
        j=1
        for i in open('users.txt').read().splitlines():
            username , userpass = i.split(' ')
            db.session.add(User(username , userpass , 'team'+str(j)))
            Teams.query.filter(Teams.teamcontainer=='team'+str(j)).update({Teams.name: username})
            j+=1
        db.session.commit()
    except:
        print('Create user error')
        pass

if __name__ == "__main__":
    init_main()