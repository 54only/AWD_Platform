import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import json
from flask import Flask
from time import strftime,localtime
from log import logset
import datetime,decimal


class JSONEncoder(json.JSONEncoder):
    def default(self, o):

        if isinstance(o,decimal.Decimal):
            return str(o)
        if isinstance(o,datetime.datetime):
            return str(o)

        return json.JSONEncoder.default(self,o)




logger = logset('models')

app = Flask(__name__)
app.json_encoder = JSONEncoder


app.secret_key = 'eIImw7u5Vi3zQu5vAwBDEiyn9ESI0Bje1xOAyEuTrTprBgI8zb3RPkFTUjGdIfGdLrx8uGKS20ITxCZX0'



app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://debian-sys-maint:Ihpz39779MWqW4zq@127.0.0.1:3306/awd?charset=utf8&autocommit=true"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:54only@127.0.0.1:3306/awdplatform?charset=utf8"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class math(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120))
    starttime = db.Column(db.DateTime)
    endtime = db.Column(db.DateTime)
    flagflash = db.Column(db.Integer)
    startscore = db.Column(db.Integer)
    atacckscore = db.Column(db.Integer)
    checkscore = db.Column(db.Integer)
    
    def __init__(self, name,starttime, endtime, flagflash,startscore=10000):
        self.name = name
        self.starttime = starttime
        self.endtime = endtime
        self.flagflash = flagflash
        self.startscore = startscore
        self.atacckscore = 200
        self.checkscore = 400




class containers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True)
    sshpassword = db.Column(db.String(120), unique=False)
    sshaccount = db.Column(db.String(120), unique=False)
    serviceport = db.Column(db.Integer, unique=True)
    sshport = db.Column(db.Integer, unique=True)
    teamid = db.Column(db.Integer)
    score = db.Column(db.DECIMAL(10,2))
    typename = db.Column(db.String(120), unique=False) 
    check_stat = db.Column(db.Integer)
    attack_stat = db.Column(db.Integer)
    def __init__(self,typename, name,sshpassword, sshaccount, serviceport,sshport,teamid,score):
        self.name = name
        self.typename = typename
        self.sshpassword = sshpassword
        self.sshaccount = sshaccount
        self.serviceport = serviceport
        self.sshport = sshport
        self.teamid = teamid
        self.score = score
        self.check_stat = 0 #0 normal , 1 checked
        self.attack_stat = 0#0 normal , 1 attacked
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

    def to_json_secrity(self):
        dict = self.__dict__

        safedic=['typename','score','check_stat','attack_stat']
        
        tmp={}
        for i in dict:
            if i in safedic:
                tmp[i]=dict[i]

        return tmp


class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    teamid = db.Column(db.Integer)
    score = db.Column(db.DECIMAL(10,2))
    rounds = db.Column(db.Integer)

    def __init__(self, teamid,score, rounds):
        self.teamid = teamid
        self.score = score
        self.rounds = rounds


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=False)
    #teamname = db.Column(db.String(120), unique=True)
    teamid = db.Column(db.Integer)
    
    def __init__(self, username, password, teamid):
        #self.teamid = teamid
        self.username = username
        self.password = hashlib.md5(password).hexdigest()
        #self.teamname = teamname
        self.teamid = teamid

    def __repr__(self):
        return '<User %r>' % self.username
        
    @classmethod
    def psw_to_md5(self, str_psw):
        import hashlib
        if str_psw == None:
            return None
        else:
            passwd = hashlib.md5(str_psw.encode(encoding='utf-8')).hexdigest()
            return passwd


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(128), unique=True)
    country = db.Column(db.String(128))
    #teamcontainer = db.Column(db.String(128), unique=True)
    token = db.Column(db.String(128), unique=True)
    sshpassword = db.Column(db.String(128))
    
    #def __init__(self,id,name,country,teamcontainer,token,sshpassword):
    def __init__(self,name,country,token,sshpassword):
        self.country=country
        self.name=name
        self.token=token
        self.sshpassword=sshpassword

    def status(self):
        self.scoresum = self.score()
        c=containers.query.filter(containers.teamid==self.id).all()
        d=[]
        for i in c:
            d.append(i.to_json_secrity())
        self.containers=d
        
        dic = self.__dict__
        if "_sa_instance_state" in dic:
            del dic["_sa_instance_state"]    
        del dic['sshpassword']    
        del dic['token']   

        return dic



    def score(self):

        return db.session.query(func.sum(containers.score)).filter(containers.teamid==self.id).first()[0]

    
    def show(self):
        return str(self)
    
    def __repr__(self):
        return ("<Teams %s>"%(self.name)).encode('utf-8') 
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]


        return dict


class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    information = db.Column(db.String(128), unique=True)

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    attackteamid = db.Column(db.Integer)
    score = db.Column(db.DECIMAL(10,2))
    rounds = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    msg = db.Column(db.Text)
    containerid = db.Column(db.Integer)

    def __init__(self,attackteamid,rounds,containerid,text,score=0):
        self.attackteamid=attackteamid
        self.rounds=rounds
        self.score=score
        self.containerid=containerid
        self.time=strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.msg = text



class Flags(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    containerid = db.Column(db.Integer)
    flag = db.Column(db.Text)
    rounds = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    def __init__(self,containerid,flag,rounds):
        self.containerid=containerid
        self.flag=flag
        self.rounds=rounds
        self.time=strftime("%Y-%m-%d %H:%M:%S", localtime())


def main(npcteams=3):
    db.drop_all()
    db.create_all()
    adminuser=User('admin','Admin@123!',0)
    db.session.add(adminuser)   
    db.session.add(math('WelCome to 54only\'s AWD Platform',localtime(), datetime.datetime.now()+datetime.timedelta(minutes=120), 1))  #datetime.timedelta(hours=3,minutes=30,seconds=30,days=3)
    db.session.commit()

    from init import init_main
    init_main(npcteams)
    logger.info('DB created')
    
if __name__ == "__main__":
    main()








