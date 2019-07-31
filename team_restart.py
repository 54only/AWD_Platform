import sys
from batch import start_docker
from models import Teams





teamid = int(sys.argv[1])
team = Teams.query.filter(Teams.teamcontainer==teamid).first()
start_docker(team)


print('team %d restarted'% teamid)