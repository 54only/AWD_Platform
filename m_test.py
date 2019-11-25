# -*- coding: utf-8 -*-
from models import db,Teams,Flags,math,Round,containers,User



c= Teams.query.count()


print c

q = User.query.join(Teams,Teams.id==User.teamid).with_entities(User.id,Teams.name).all()


#q = db.session.query(User).join(Teams,Teams.id=User.teamid).all()
print q



for i in q:
    print i









