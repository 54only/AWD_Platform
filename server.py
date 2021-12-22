# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for,abort, session,flash
from flask_login import UserMixin, LoginManager, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import aliased
from models import *
from log import logger
from batch import *
from dockercontr import *
import socket
import pymysql
import traceback
import time
import datetime
import sys
import json
import team_restart

reload(sys)
sys.setdefaultencoding('utf-8')











login_manager = LoginManager()
login_manager.init_app(app)



login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message = "Please LOG IN"
login_manager.login_message_category = "info"






def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


#app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:foru83614@127.0.0.1:3306/awd?charset=utf8&autocommit=true"


#app.config['JSON_AS_ASCII'] = False
#db = SQLAlchemy(app)


#print(User.query.all())
#print(Teams.query.all())
#print(Teams.query.first().country)
#print('!@!!!!!',Flags.query.order_by(Flags.rounds.desc()).first().rounds)
@app.route('/1')
@login_required
def index_back():
    #print session
    return render_template('base.html')

@app.route('/')
@login_required
def index():
    #print session
    return render_template('index.html')


@app.route('/index')
@login_required
def index_show():
    #print session
    return render_template('index_show.html')

@app.route('/scores')
@login_required
def show_scores():

    scores2 = db.session.query(Teams.name,Scores.score,Scores.rounds).join(Teams,Teams.id==Scores.teamid).order_by(Scores.teamid,Scores.rounds).all()

    msgdic={}


    for i in scores2:
        if msgdic.get(i[0]):
            msgdic[i[0]].append(i[1])
        else:
            msgdic[i[0]]=[]
            msgdic[i[0]].append(i[1])


    return jsonify(msgdic)



@app.route('/timedelta')
@login_required
def timedelta():
    
    mathmsg=math.query.first()
    msg={}
    msg['starttime']=mathmsg.starttime.strftime( '%Y-%m-%d %H:%M')  
    msg['endtime']=mathmsg.endtime.strftime( '%Y-%m-%d %H:%M')  
    msg['flagflash']=mathmsg.flagflash
    
    if (mathmsg.starttime - datetime.datetime.now()).total_seconds()>0:
        msg['timeleft']=str(mathmsg.starttime-datetime.datetime.now()).split('.')[0]
        msg['timecount']=int((mathmsg.starttime-datetime.datetime.now()).total_seconds())
    else:
        msg['timeleft']=str(mathmsg.endtime-datetime.datetime.now()).split('.')[0]
        msg['timecount']=int((mathmsg.endtime-datetime.datetime.now()).total_seconds())


    #msg['timecount']=int((mathmsg.endtime-datetime.datetime.now()).total_seconds())
    msg['now']=datetime.datetime.now().strftime( '%Y-%m-%d %H:%M') 
    msg['startscore']=mathmsg.startscore
    msg['name']=mathmsg.name
    msg['checkscore']=mathmsg.checkscore
    msg['atacckscore']=mathmsg.atacckscore

    if str(mathmsg.endtime-datetime.datetime.now()).startswith('-'):
        msg['timeleft']='比赛已经结束'


    return jsonify(msg)
    #return render_template('base.html', ip=get_host_ip())


def query_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return True
    return False

@login_manager.user_loader
def user_loader(username):
    if query_user(username):
        user = Users()
        user.id = username
        return user
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("login.html", error="Registration allowed!")
    teamnum = Teams.query.count()
    try:
        usernum = User.query.count()
    except:
        usernum = 0
    #print(usernum,teamnum)
    
    if usernum < teamnum:
        if request.method == 'GET':
            return render_template('register.html')
        else:
            username = request.form['username']
            password = User.psw_to_md5(request.form['password'])
            teamname = request.form['teamname']
            
            if username is None or password is None:
                return render_template("register.html", error="Username or Password error")
            if User.query.filter_by(username = username).first() is not None:
                return render_template("register.html", error="Username already exists")
            elif User.query.filter_by(teamname = teamname).first() is not None:
                return render_template("register.html", error="TeamName already exists")

            else:
                try:
                    teamid = User.query.count()
                except:
                    teamid = 0
                teamid+=1
                user = User(teamid,username,password,teamname)
                db.session.add(user)
                db.session.commit()
                teamid = User.query.filter(User.username==username).with_entities(User.teamid).all()[0][0]
                teamname = User.query.filter(User.username==username).with_entities(User.teamname).all()[0][0]
                while True:
                    teamnames = Teams.query.filter(Teams.id==teamid).with_entities(Teams.name).all()[0][0]
                    if teamnames != teamname:
                        Teams.query.filter(Teams.id==teamid).update({Teams.name: teamname})
                    else:
                        break
                return render_template("login.html", right="Register successfully, please login")
    else:
        return render_template("login.html", error="The team is full, No registration allowed!")

class Users(UserMixin):
    pass

@app.route('/login_back', methods=['GET', 'POST'])
def login_back():
    user_id = session.get('user_id')
    #print(user_id)
    if request.method == 'GET':
        #user = User.query.all()
        #print user
        return render_template("login.html")
    else:
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        #if (current_user.is_authenticated and user ):
        #    logout_user()
        #    return redirect(url_for('index'))

    if user == None:
        return render_template("login.html", error="username or password error")
    pw_form = User.psw_to_md5(request.form['password'])
    pw_db = user.password
    #print(pw_form,pw_db)

    if pw_form == pw_db:
        session['teamid']=user.teamid
        user = Users()
        user.id = username
        login_user(user, remember=True)
        
        flash('Logged in successfully')
        return redirect(url_for('index'))
    return render_template("login.html", error="username or password error")

       
@app.route('/login', methods=['GET', 'POST'])
def login():
    user_id = session.get('user_id')
    #print(user_id)
    if request.method == 'GET':
        #user = User.query.all()
        #print user
        return render_template("login2.html")
    else:
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        #if (current_user.is_authenticated and user ):
        #    logout_user()
        #    return redirect(url_for('index'))

    if user == None:
        return render_template("login2.html", error="username or password error")
    pw_form = User.psw_to_md5(request.form['password'])
    pw_db = user.password
    #print(pw_form,pw_db)

    if pw_form == pw_db:
        session['teamid']=user.teamid
        user = Users()
        user.id = username
        login_user(user, remember=True)
        
        flash('Logged in successfully')
        return redirect(url_for('index'))
    return render_template("login2.html", error="username or password error")




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin2ee24916bf1bafd60cd58b8555a53a9e', methods=['GET'])
@login_required
def admin():
    if session.get('user_id') != 'admin':
        return render_template("login2.html", error="No privileges")
    else:
        return render_template('base_admin.html')


@app.route('/admin2ee24916bf1bafd60cd58b8555a53a9e/math', methods=['GET', 'POST'])
@login_required
def admin_math():
    if session.get('user_id') != 'admin':
        return render_template("login2.html", error="No privileges")
    else:
        themath = math.query.first()
        if request.method=='POST':
            name=request.form['name'];
            endtime=request.form['endtime'];
            starttime=request.form['starttime'];
            flagflash=request.form['flagflash'];
            startscore = request.form['startscore'];
            atacckscore = request.form['atacckscore'];
            checkscore = request.form['checkscore'];
            
            themath.endtime=endtime
            themath.starttime=starttime
            themath.flagflash=flagflash
            themath.startscore=startscore
            themath.name=name
            themath.atacckscore=atacckscore
            themath.checkscore=checkscore

            db.session.commit()

            return render_template('math.html')
        else:
            return render_template('math.html',name=themath.name)


@app.route('/admin2ee24916bf1bafd60cd58b8555a53a9e/contanerlist', methods=['GET', 'POST'])
def contanerlist():
    contanerlist = db.session.query(
        containers.name,containers.score,containers.check_stat,containers.attack_stat,Teams.name.label('TeamName')
        ).join(Teams,Teams.id == containers.teamid).order_by(Teams.name).all()
    # r = []
    # for i in contanerlist   :
    #     print i.name,float(round(i.score*100)/100),i.check_stat,i.attack_stat,i.TeamName
    #     r.append({
    #     'name':'1',#i.name.encode('utf8'),
    #     'score':100,#float(round(i.score*100)/100),
    #     'check_stat':i.check_stat,
    #     'attack_stat':i.attack_stat,
    #     'TeamName':'x'#i.TeamName.encode('utf8')
    #     })
    # r=[]
    # print r
    # r0=[]
    return render_template('dockers.html',contanerlist=contanerlist)
    #return render_template("dockers.html")

@app.route('/admin2ee24916bf1bafd60cd58b8555a53a9e/contanerrestart', methods=['GET','POST'])
def restart_container():
    if session.get('user_id') != 'admin':
        return render_template("login2.html", error="No privileges")
    containername=request.form['containername']
    logger.info('Container restarting ... %s ' % containername)
    print 'Container restarting ... %s ' % containername
    #return containername
    #containername = 'pwn_simple_4'
    r = team_restart.main(containername)
    return r


@app.route('/admin2ee24916bf1bafd60cd58b8555a53a9e/info', methods=['GET', 'POST'])
@login_required
def info():

    if session.get('user_id') != 'admin':
        return render_template("login2.html", error="No privileges")

    info1 = Info.query.order_by('id').all()
    infolist = list()
    msg = dict()
    for i in info1:
        msg = {
            'id':i.id,
            'information':i.information,
        }
        infolist.append(msg)
    
    if request.method == 'GET':
        return render_template('info.html',infolist=infolist)
    else:
        information = request.form['information']
        try:
            info2 = Info.query.filter_by(information = information).first_or_404()
        except:
            user = None
        if information:
            if Info.query.filter_by(information = information).first() is not None:
                return render_template("info.html" , error="information already exists")
        if information:
            infor = Info(information = information)
            db.session.add(infor)
            db.session.commit()
            try:
                id = msg['id']
            except:
                id=0
            infolist.append({'id':id+1,'information':information})
        return render_template('info.html',infolist=infolist[: :-1])


@app.route('/info/<id>', methods=['GET', 'POST'])
def info_pro(id):
    if request.method == 'GET':
        info1 = Info.query.order_by(Info.id.desc()).all()
        infolist = list()
        for i in info1:
            msg = {'id':i.information}
            infolist.append(msg)
        return  json.dumps(infolist,ensure_ascii=False) 
    else:
        if session.get('user_id') != 'admin':
            return render_template("login2.html", error="No privileges")
        
        Info.query.filter_by(id = id).delete()
        db.session.commit()
        return redirect('/info')




@app.route('/team', methods=['GET'])
def showteam():
    teamlist=list()
    try:
        teamid = session.get('teamid')
        #teamid = User.query.filter(User.username==user_id).with_entities(User.teamname).all()[0][0]
        #team = Teams.query.filter(Teams.teamcontainer == teamid).first()
        mycontainers = containers.query.filter(containers.teamid==teamid).all()

        #print mycontainers
        for team in mycontainers:
            msg = team.to_json()
            #print msg
            teamlist.append(msg)
    except:
        return '获取 id 出错'

    msg={}
    t = Teams.query.filter(Teams.id == teamid).first_or_404()
    msg['teamname'] = t.name
    msg['token'] = t.token
    msg['containers'] = teamlist

    #print teamlist
    return jsonify(msg)
    #return json.dumps(teamlist, ensure_ascii=False)

@app.route('/teams', methods=['GET'])
def showteams():
    
    mathmsg=math.query.first()

    if not mathmsg:
        print 'Error Get mathmsg'
        return False


    teamlist = list()
    #teamnum = User.query.count()
    
    teams = Teams.query.all()
    
    #print(teams[0].score())
    teamlist2 = []
    for team in teams:
        msg = team.status()
        #roundscore = team.score_delta()
        teamlist2.append(msg)  

    #print teamlist2
    teamlist = (sorted(teamlist2,key=lambda x:x['scoresum'],reverse = True))
    #print('team')
    j=1
    for i in teamlist:
        i['rank']=j
        j+=1
        #if session.get('user_id') == i['name']:
        #    break
    #print i,session.get('user_id')

    rtn={}

    typename = db.session.query(func.distinct(containers.typename)).all()

    #print typename
    #print typename[0][0],len(typename),len(typename[0])

    rtn['teams']=teamlist
    rtn['typename']=[]

    for i in typename:
        #print i
        rtn['typename'].append(i[0])


    return jsonify(rtn)

@app.route('/teamall', methods=['GET'])
def showteamss():
    teamlist=list()
    teamnum = Teams.query.filter(Teams.id>=0).count()
    for teamid in range(1,teamnum+1):
        team = Teams.query.filter(Teams.id==teamid).first()
        #print(team.show())
        msg={'id':team.id,
            'name':team.name,
            'country':team.country,
            'token':team.token,
            'ssh-user':'www-data',
            'ssh-password':team.sshpassword,
            'score':team.score(),
            'ssh-port':30022+team.id*100,
            'web-port':30080+team.id*100
            }
        
        teamlist.append(msg)
    return json.dumps(teamlist,ensure_ascii=False) 

'''
@app.route('/')
def index():
    msg = '<title>Awdplaform</title><h1>Welcome to awdplaform</h1><hr>'
    msg += "<h2>提交flag方法</br>POST</br> http://"+get_host_ip()+":9000/flag?token=TOKEN</br>flag=flag</h2><hr>"
    msg += '<p><a href="/teamscores">得分板</a></p>'
    msg += '<p><a href="/rounds">查看日志</a></p>'
    for i in range(1,5):
        msg += '<p><a href="/team?teamid={id}">查看team{id}信息</a></p>'.format(id=i)

    return msg

def showteam():
    teamlist=list()
    teamnum = Teams.query.filter(Teams.id>=0).count()
    for teamid in range(1,teamnum+1):
        team = Teams.query.filter(Teams.id==teamid).first()
        #print(team.show())
        msg={'id':team.id,
            'name':team.name,
            'country':team.country,
            'token':team.token,
            'ssh-user':'www-data',
            'ssh-password':team.sshpassword,
            'score':team.score(),
            'ssh-port':30022+team.id*100,
            'web-port':30080+team.id*100
            }
        
        teamlist.append(msg)
    return teamlist



@app.route('/teamscores', methods=['GET'])
def showteamscores():
    #teamid = request.args.get('teamid')

    teams =  Teams.query.all()
    msg={}
    i=0
    for team in teams:
        i+=1

        #team = Teams.query.filter(Teams.id==teamid).first()
        #print(team.show())
        msg[i]={#'id':team.id,
            #'name':team.name,
            #'country':team.country,
            #'token':team.token,
            #'ssh-user':'www-data',
            #'ssh-password':team.sshpassword,
            'score':team.score(),
            'ssh-port':30022+team.id*100,
            'web-port':30080+team.id*100
            }
        #return json.dumps(msg,ensure_ascii=False) 
    #else:
    #    msg={'message':'request error,please get with param ,example ?teamid=xxx'}
    return jsonify(msg)
    return json.dumps(msg,ensure_ascii=False) 
'''

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj) 

@app.route('/rounds2', methods=['GET'])
def showrounds2():
    Rounds2 = db.session.query(Round.time,Teams.name,containers.typename).join(Teams,Teams.id==Round.attackteamid).join(containers,containers.id==Round.containerid).filter(containers.teamid==session.get('teamid')).order_by(Round.time.desc()).limit(10).all()
    #print Rounds2
    #print session
    msg2=[]
    for i in Rounds2:
        msg2.append({'teamname':i[1],'typename':i[2],'time':i[0]})
        

    return jsonify(msg2)


@app.route('/rounds', methods=['GET'])
def showrounds():

    #Rounds = Round.query.join(Teams,Teams.id==Round.attackteamid).order_by(Round.id.desc()).limit(10).all()
    a_alias = aliased(Teams)

    Rounds = db.session.query(Round.id.label('id'), 
        Round.score.label('score'),
        Round.rounds.label('rounds'),
        Round.msg.label('msg'),
        Round.time.label('time'),
        containers.typename.label('typename'),
        Round.attackteamid.label('attackteamid'),
        containers.teamid.label('defanseteamid'),
        Teams.name.label('attackteamname'),
        a_alias.name.label('defanseteamname')
        ).join(Teams,Teams.id==Round.attackteamid).join(containers,containers.id==Round.containerid).join(a_alias,a_alias.id==containers.teamid).order_by(Round.id.desc()).limit(20).all()
    #Rounds2 = db.session.query(Round.id,Teams.name,containers.typename,containers.teamid).join(Teams,Teams.id==Round.attackteamid).join(containers,containers.id==Round.containerid).all()
    #print Rounds2
    msg = {}
    msg2 = []
    #print Rounds[0].__dict__
    for i in Rounds:
        msg[i.id] = {'id': i.id,
                     'score': i.score,
                     'rounds': i.rounds,
                     'msg': i.msg,
                     'time': i.time,
                     }
        msg2.append({'id': i.id,
                     'score': i.score,
                     'rounds': i.rounds,
                     'msg': i.msg,
                     'time': i.time,
                     'typename': i.typename,
                     'attackteamid': i.attackteamid,
                     'defanseteamid': i.defanseteamid,
                     'attackteamname': i.attackteamname,
                     'defanseteamname': i.defanseteamname,

                     })
        #print i.query
        
    return jsonify(msg2)



@app.route('/attackshow', methods=['GET'])
def attackshow():

    #Rounds = Round.query.join(Teams,Teams.id==Round.attackteamid).order_by(Round.id.desc()).limit(10).all()
    a_alias = aliased(Teams)
    querytime = datetime.datetime.now() - datetime.timedelta(seconds=20)
    Rounds = db.session.query(Round.id.label('id'), 
        Round.score.label('score'),
        Round.rounds.label('rounds'),
        Round.msg.label('msg'),
        Round.time.label('time'),
        containers.typename.label('typename'),
        Round.attackteamid.label('attackteamid'),
        containers.teamid.label('defanseteamid'),
        Teams.name.label('attackteamname'),
        a_alias.name.label('defanseteamname')
        ).join(Teams,Teams.id==Round.attackteamid).join(containers,containers.id==Round.containerid).join(a_alias,a_alias.id==containers.teamid).filter(Round.time>=querytime).order_by(Round.id.desc()).all()
    #Rounds2 = db.session.query(Round.id,Teams.name,containers.typename,containers.teamid).join(Teams,Teams.id==Round.attackteamid).join(containers,containers.id==Round.containerid).all()
    #print Rounds2
    msg = {}
    msg2 = []
    #print Rounds[0].__dict__
    for i in Rounds:
        msg[i.id] = {'id': i.id,
                     'score': i.score,
                     'rounds': i.rounds,
                     'msg': i.msg,
                     'time': i.time,
                     }
        msg2.append({'id': i.id,
                     'score': i.score,
                     'rounds': i.rounds,
                     'msg': i.msg,
                     'time': i.time,
                     'typename': i.typename,
                     'attackteamid': i.attackteamid,
                     'defanseteamid': i.defanseteamid,
                     'attackteamname': i.attackteamname,
                     'defanseteamname': i.defanseteamname,

                     })
        #print i.query
        
    return jsonify(msg2)








@app.route('/current_rounds', methods=['GET'])    
def showcurrent_rounds():   
    current_rounds = Flags.query.order_by(Flags.rounds.desc()).limit(1).first()
    
    if current_rounds:    
        return jsonify(current_rounds.rounds)
    else:
        return jsonify(0)
    

@app.route('/flag', methods=['GET', 'POST'])
def flagcheck():
    msg = {'status': 0, 'msg': '提交成功'}
    themath = math.query.first()
    if themath:
        if (datetime.datetime.now()-themath.endtime).total_seconds() > 0 :
            msg['status']=-1
            msg['msg']='比赛已经结束'
            return json.dumps(msg, ensure_ascii=False)
        if (datetime.datetime.now()-themath.starttime).total_seconds() < 0 :
            msg['status'] = -1
            msg['msg'] = '比赛尚未开始'
            return json.dumps(msg, ensure_ascii=False)
    else:
        msg['status'] = -1
        msg['msg'] = '比赛信息有误，请联系管理员'
        return json.dumps(msg, ensure_ascii=False)

    

    lastround = Flags.query.order_by(Flags.rounds.desc()).first()  # .rounds
    #print(lastround)
    #print('lastround',lastround)

    if lastround:
        lastround = lastround.rounds
    else:
        msg['status'] = -1
        msg['msg'] = '比赛尚未开始'
        return json.dumps(msg, ensure_ascii=False)
    token = request.args.get('token')

    try:
        flag = request.form['flag']
    except:
        msg['status'] = -1
        msg['msg'] = '提交格式不正确'
        return json.dumps(msg, ensure_ascii=False)

    #print(token,flag)

    attackteam = Teams.query.filter(Teams.token == token).first()
    
    #print(attackteam)

    if attackteam:
        attackteamid = attackteam.id
    else:
        msg['status'] = -1
        msg['msg'] = 'TOKEN 错误'
        return json.dumps(msg, ensure_ascii=False)

    #print(attackteamid)

    attacked_container = Flags.query.filter( Flags.rounds == lastround, Flags.flag == flag).first()
    #print('attackteamid', attackteamid)
    #print('rounds', lastround)
    #print('flag', flag)
    
    #for i in Flags.query.filter(Flags.rounds == lastround).all():
    #    print(i.flag)
    
    
    if attacked_container:
        attacked_container = containers.query.filter(containers.id == attacked_container.containerid).first()
        #print(len(attacked_container))
        
        if not attacked_container:
        #attackteamid = Teams.query.filter(Teams.id == attackteam.id).first()
            msg['status'] = -1
            msg['msg'] = 'FLAG 错误'
            return json.dumps(msg, ensure_ascii=False)
        else:
            dteam = Teams.query.filter(Teams.id == attacked_container.teamid).first()
    else:
        msg['status'] = -1
        msg['msg'] = 'FLAG 错误'
        return json.dumps(msg, ensure_ascii=False)

    if attacked_container.teamid == attackteam.id:
        msg['status'] = -1
        msg['msg'] = '你不能攻击自己的队伍'
        return json.dumps(msg, ensure_ascii=False)

    roundcheck = Round.query.filter(Round.attackteamid == attackteam.id,
                                    Round.containerid == attacked_container.id, Round.rounds == lastround).first()

    if roundcheck:
        msg['status'] = -1
        msg['msg'] = '你已经攻击了该的队伍'
        return json.dumps(msg, ensure_ascii=False)
        
    #print(defenseteamid)
    #msg = 'rounds {} attackteamid {} defenseteamid {}'.format(lastround,attackteamid,defenseteamid)
    msg['status'] = 1
    msg['msg'] = '提交成功，{} 成功攻击了 {} 的 {}'.format(
        attackteam.name, dteam.name,attacked_container.typename) 


    rd = Round(attackteamid,lastround, attacked_container.id,
               '{} 攻击了 {} 的 {}'.format(attackteam.name, dteam.name,attacked_container.typename))
    db.session.add(rd)
    attacked_container.attack_stat = 1
    db.session.commit()
    # 这里是后加的.通过队伍Flag已经被提交,就不得分的机制,直接更新分数200
    #Round.query.filter(Round.score==0).update({Round.score : 200})
    #db.session.commit()
    logger.info('{} 攻击了 {} 的 {}'.format(attackteam.name, dteam.name,attacked_container.typename))
    return json.dumps(msg, ensure_ascii=False)


if __name__ == '__main__':
    #exit()
    app.run(debug=True, host='0.0.0.0', port=9000)
