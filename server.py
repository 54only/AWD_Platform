# -*- coding: utf-8 -*-
from flask import Flask, request, json, jsonify, render_template, make_response, redirect, url_for,abort, session,flash
from flask_login import UserMixin, LoginManager, login_required, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
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


app.config['JSON_AS_ASCII'] = False
#db = SQLAlchemy(app)


#print(User.query.all())
#print(Teams.query.all())
#print(Teams.query.first().country)
#print('!@!!!!!',Flags.query.order_by(Flags.rounds.desc()).first().rounds)
@app.route('/')
@login_required
def index():
    return render_template('base.html', ip=get_host_ip())


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

@app.route('/login', methods=['GET', 'POST'])
def login():
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
        user = Users()
        user.id = username
        login_user(user, remember=True)
        flash('Logged in successfully')
        return redirect(url_for('index'))
    return render_template("login.html", error="username or password error")

        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        return render_template('other.html')

@app.route('/info', methods=['GET', 'POST'])
@login_required
def info():
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
        Info.query.filter_by(id = id).delete()
        db.session.commit()
        return redirect('/info')


@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add():
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        usernum = User.query.count()
        if request.method == 'GET':
            # 如果是GET请求，则渲染创建页面
            return render_template('add.html',usernum=usernum+1)
        else:
            teamid = request.form['teamid']
            username = request.form['username']
            password = User.psw_to_md5(request.form['password'])
            teamname = request.form['teamname']
            try:
                user = User.query.filter_by(username = username).first_or_404()
            except:
                user = None
            #return(str(username+password+teamname))
    
            if username and teamname and password:
                if User.query.filter_by(username = username).first() is not None:
                    return render_template("add.html" ,user = user, error="Username already exists")
                if User.query.filter_by(teamname = teamname).first() is not None:
                    return render_template("add.html",user = user, error="TeamName already exists")
                
                user = User( username = username, password = password, teamname = teamname)
                
                db.session.add(user)
                db.session.commit()
                Teams.query.filter(Teams.teamcontainer==teamname).update({Teams.name: username})
                db.session.commit()
                return redirect('/admin/user')
            else:
                return render_template("add.html", user = user, error="Username or Password error")
    


@app.route('/admin/delete/<id>', methods=['GET'])
@login_required
def delete(id):
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        User.query.filter_by(teamid = id).delete()
        db.session.commit()
        return redirect('/admin/user')



@app.route('/admin/update/<id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        user = User.query.filter_by(teamid = id).first_or_404()
        if request.method == 'GET':
            return render_template('update.html',user = user)
        else:
            username = request.form['username']
            password = User.psw_to_md5(request.form['password'])
            teamname = request.form['teamname']
            #return(str(username+password+teamname))
            if username and teamname and password:
    
                if User.query.filter_by(username = username).first() is not None:
                    return render_template("update.html" ,user = user, error="Username already exists")
                if User.query.filter_by(teamname = teamname).first() is not None:
                    return render_template("update.html",user = user, error="TeamName already exists")
                User.query.filter_by(teamid = id).update({'username':username,'password':password,'teamname':teamname})
                
                Teams.query.filter(Teams.teamcontainer==teamname).update({Teams.name: username})
                db.session.commit()
                return redirect('/admin/user')
            else:
                return render_template("update.html", user = user, error="Username or Password error")

@app.route('/admin/team')
@login_required
def teamlist():
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        teams = Teams.query.all()
        teamlist=list()
        for team in teams:
            msg={
                'id':team.id,
                'name':team.name,
                'token':team.token,
                'sshpassword':team.sshpassword,
            }
            teamlist.append(msg)
        return render_template('team.html', teamlist = teamlist)


@app.route('/admin/teamadd', methods=['GET'])
@login_required
def teamadd():
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        teamnum = Teams.query.count()
        id = teamnum+1
        name = 'NPC'+str(id)
        teamcontainer = 'team'+str(id)
        tokens = make_token_str(teamcontainer)
        sshpassword= make_token_str(teamcontainer)
        team = Teams(id = id, name = name, country='',teamcontainer=teamcontainer,token=tokens,sshpassword = sshpassword)
        db.session.add(team)
        db.session.commit()
        start_docker(team)
        return redirect('/admin/team')


@app.route('/admin/team/reset/<id>', methods=['GET'])
@login_required
def resetteam(id):
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        team = Teams.query.filter(Teams.id==id).first()
        start_docker(team)
        return redirect('/admin/team')


@app.route('/admin/team/delete/<id>', methods=['GET'])
@login_required
def deleteteam(id):
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        team = Teams.query.filter(Teams.id==id).first()
        clear_container(team.teamcontainer)
        Flags.query.filter(Flags.teamid == id).delete()
        User.query.filter(User.teamid == id).delete()
        Teams.query.filter(Teams.id == id).delete()
        db.session.commit()
        return redirect('/admin/team')


@app.route('/admin/user')
@login_required
def userlist():
    if session.get('user_id') != 'admin':
        return render_template("login.html", error="No privileges")
    else:
        users = User.query.all()
        userlist=list()
        for user in users:
            msg={
                'teamid':user.teamid,
                'username':user.username,
                'password':user.password,
                'teamname':user.teamname,
            }
            userlist.append(msg)
        return render_template('user.html', userlist = userlist)




@app.route('/team', methods=['GET'])
def showteam():
    teamlist=list()
    try:
        user_id = session.get('user_id')
        teamid = User.query.filter(User.username==user_id).with_entities(User.teamname).all()[0][0]
        team = Teams.query.filter(Teams.teamcontainer == teamid).first()
        msg = {
            'ip': get_host_ip(),
            'id': team.id,
            'name': team.name,
            'country': team.country,
            'token': team.token,
            'ssh-user': 'www-data',
            'ssh-password': team.sshpassword,
            'score': team.score(),
            'ssh-port': 30022+team.id*100,
            'web-port': 30080+team.id*100
        }
        teamlist.append(msg)
    except:
        return '获取 id 出错'
    return json.dumps(teamlist, ensure_ascii=False)

@app.route('/teams', methods=['GET'])
def showteams():
    teamlist = list()
    teamnum = User.query.count()
    
    teams = Teams.query.all()
    
    #print(teams[0].score())
    teamlist2 = []
    for team in teams:
        msg = {
            'ip': get_host_ip(),
            'id': team.id,
            'name': team.name,
            'country': team.country,
            'token': team.token,
            'score': team.score(),
            'ssh-port': 30022+team.id*100,
            'web-port': 30080+team.id*100
        }
        teamlist2.append(msg)    
    teamlist = (sorted(teamlist2,key=lambda x:x['score'],reverse = True))
    #print('team')
    return json.dumps(teamlist, ensure_ascii=False)

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
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj) 

@app.route('/rounds', methods=['GET'])
def showrounds():

    Rounds = Round.query.order_by(Round.id.desc()).limit(20).all()
    msg = {}
    msg2 = []

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
                     })
    return json.dumps(msg2, ensure_ascii=False,cls=DateEncoder)

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

    print(token,flag)

    attackteam = Teams.query.filter(Teams.token == token).first()
    
    print(attackteam)

    if attackteam:
        attackteamid = attackteam.id
    else:
        msg['status'] = -1
        msg['msg'] = 'TOKEN 错误'
        return json.dumps(msg, ensure_ascii=False)

    #print(attackteamid)

    defenseteam = Flags.query.filter(
        Flags.rounds == lastround, Flags.flag == flag).first()
    print('rounds', lastround)
    print('flag', flag)
    for i in Flags.query.filter(Flags.rounds == lastround).all():
        print(i.flag)

    if defenseteam:
        defenseteamid = defenseteam.teamid
        defenseteam = Teams.query.filter(Teams.id == defenseteamid).first()
    else:
        msg['status'] = -1
        msg['msg'] = 'FLAG 错误'
        return json.dumps(msg, ensure_ascii=False)

    if defenseteamid == attackteamid:
        msg['status'] = -1
        msg['msg'] = '你不能攻击自己的队伍'
        return json.dumps(msg, ensure_ascii=False)

    roundcheck = Round.query.filter(Round.defenseteamid == defenseteamid,
                                    Round.attackteamid == attackteamid, Round.rounds == lastround).first()

    if roundcheck:
        msg['status'] = -1
        msg['msg'] = '你已经攻击了该的队伍'
        return json.dumps(msg, ensure_ascii=False)
        
    roundcheck2 = Round.query.filter(Round.score == 200,Round.defenseteamid == defenseteamid ,Round.rounds == lastround).first()
    if roundcheck2:
        msg['status'] = -1
        msg['msg'] = '该队伍Flag已经被提交'
        return json.dumps(msg, ensure_ascii=False)
    #print(defenseteamid)
    #msg = 'rounds {} attackteamid {} defenseteamid {}'.format(lastround,attackteamid,defenseteamid)
    msg['status'] = 1
    msg['msg'] = '提交成功，({})成功攻击了 {}'.format(
        attackteam.name, defenseteam.name) 
    rd = Round(attackteamid, defenseteamid, lastround,
               '{} 攻击了 {}'.format(attackteam.name, defenseteam.name))
    db.session.add(rd)
    db.session.commit()
    # 这里是后加的.通过队伍Flag已经被提交,就不得分的机制,直接更新分数200
    #Round.query.filter(Round.score==0).update({Round.score : 200})
    #db.session.commit()
    logger.info('{} 成功攻击了 {}'.format(attackteam.name, defenseteam.name))
    return json.dumps(msg, ensure_ascii=False)


if __name__ == '__main__':
    #exit()
    app.run(debug=True, host='0.0.0.0', port=9000)
