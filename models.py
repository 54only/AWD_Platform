import hashlib
from flask_sqlalchemy import SQLAlchemy
import json
from flask import Flask
from time import strftime,localtime
from log import logger



app = Flask(__name__)
app.secret_key = 'eIImw7u5Vi3zQu5vAwBDEiyn9ESI0Bje1xOAyEuTrTprBgI8zb3RPkFTUjGdIfGdLrx8uGKS20ITxCZX0'



app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://debian-sys-maint:Ihpz39779MWqW4zq@127.0.0.1:3306/awd?charset=utf8&autocommit=true"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:54only@127.0.0.1:3306/awdplatform?charset=utf8"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class User(db.Model):
    teamid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=False)
    teamname = db.Column(db.String(120), unique=True)
    
    def __init__(self, username, password, teamname):
        #self.teamid = teamid
        self.username = username
        self.password = hashlib.md5(password).hexdigest()
        self.teamname = teamname

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
    teamcontainer = db.Column(db.String(128), unique=True)
    token = db.Column(db.String(128), unique=True)
    sshpassword = db.Column(db.String(128))
    
    def __init__(self,id,name,country,teamcontainer,token,sshpassword):
        self.id=id
        self.name=name
        self.country=country
        self.teamcontainer=teamcontainer
        self.token=token
        self.sshpassword=sshpassword

    def score(self,score_start=10000):
        score = db.func.sum(Round.score).label('score')
        teamadd = db.session.query(Round.attackteamid, score).filter(Round.attackteamid == self.id).first()
        teamlost = db.session.query(Round.defenseteamid, score).filter(Round.defenseteamid == self.id).first()
        return score_start+int(teamadd.score or 0) - int(teamlost.score or 0)

    
    def show(self):
        return str(self)
    
    def __repr__(self):
        return "<Teams %r>"%(self.name) 

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    score = db.Column(db.Integer)

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    information = db.Column(db.String(128), unique=True)

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    attackteamid = db.Column(db.Integer)
    defenseteamid = db.Column(db.Integer)
    score = db.Column(db.Integer)
    rounds = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    msg = db.Column(db.Text)

    def __init__(self,attackteamid,defenseteamid,rounds,text,score=0):
        self.attackteamid=attackteamid
        self.defenseteamid=defenseteamid
        self.rounds=rounds
        self.score=score
        self.time=strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.msg = text


class Flags(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    teamid = db.Column(db.Integer, db.ForeignKey('teams.id'))
    flag = db.Column(db.Text)
    rounds = db.Column(db.Integer)
    time = db.Column(db.DateTime)
    def __init__(self,teamid,flag,rounds):
        self.teamid=teamid
        self.flag=flag
        self.rounds=rounds
        self.time=strftime("%Y-%m-%d %H:%M:%S", localtime())


def main(teams=10):
    db.drop_all()
    db.create_all()
    from init import init_main
    init_main(teams)
    import batch
    batch.main()
    print("db created")
    logger.info('db created')
    
if __name__ == "__main__":
    main()








