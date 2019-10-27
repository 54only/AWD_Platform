# CTF-AWD 训练平台

[TOC]

## 项目简介

基于python+docker的AWD平台，用于内部对抗训练以及培训使用。

![](img/1.png)
![](img/2.png)
![](img/3.png)
## 特点

- docker化，简易部署
- 可部署在公网上，远程AWD攻防
- 训练环境可自定义扩展
- 10支队伍建议内存保障在6G以上

## 基本使用方式
* 准备 docker 服务
* 准备 mysql ，并建立 awd 数据库
```
pip install -r requirements.txt
```
* 编辑 model.py 修改数据库配置
```
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://debian-sys-maint:Ihpz39779MWqW4zq@127.0.0.1:3306/awd?charset=utf8&autocommit=true"          # 设定数据库用户密码
```
* 编辑 users.txt
```
teamname username userpassword   # 设定队伍账号密码
```
* 编辑 start.py
```
teams = 10          # 设定比赛环境数量，建议比赛环境数量多于队伍数量
```

* 启动比赛环境
```
python start.py     # 一键启动比赛环境
python server.py    # 启动竞赛平台
```

* 退出环境
```
python stop.py

#由于docker的卷比较占磁盘空间，建议本环境只提供比赛docker，方便将多余的container和卷一起删除，stop.py执行完后在shell中执行下面命令

docker container prune && docker volume rm $(docker volume ls -qf dangling=true)
```

## 自定义比赛环境

dockercontr.py

## 规则
* 主机信息

   * 队伍分配主机，通过指定的端口和密码进行连接
   * 主机上运行一个web或多个服务，需要选手保证其可用性审计代码，攻击其他队伍
   * 通过漏洞获取其他队伍主机权限，读取服务器上的flag并提交到flag服务器

* 攻击检测

   * 每次成功攻击，攻击队伍可平分该flag的200分，被攻击者扣除200分，轮询时间1分钟
   * 选手需要保证己方服务的可用性，服务故障扣除200分，被服务无故障的队伍平分，轮询时间1分钟
   * 得分在下一轮开始时计算

* 其他

   * 选手可以获取所有的攻击情况以及当前的分数，刷新间隔1分钟
   * 不允许使用任何形式的DOS攻击


## 更新

### 2019-10-28 

* 版本重大更新，核心代码重构
* user.txt 添加队伍名
* 一只队伍同时开启多个awd环境
* check状态和被攻击状态展示
* 取消自动 pull images，需要管理员提前做好镜像
* 添加后台功能，可以设置比赛标题、开始及结束时间、每个环境起始分数，被攻击扣分，被check扣分，即时生效
* bugs fixed
* 太晚了，队伍功能暂时放一下，队伍重启功能准备放到后台管理执行，下次更新



### 2019-10-13 

* 修复环境初始化吊死的问题
* 解决mysql容器只能建立23个的问题，需要执行 ```sudo sysctl -w fs.aio-max-nr=2097152```


## 捐助

如果您觉得该训练平台对您有帮助，欢迎给予我们一定的捐助，也是帮助该训练平台更好的发展。

![](img/11.jpg)

![](img/22.jpg)

## 捐助墙

日期 | 捐助者 | 金额
:-: | :-: | :-: | :-: 
2019.10.10 | *璇 | 0.4 




