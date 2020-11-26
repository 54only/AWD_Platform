import sys
from batch import start_docker
from models import db,Teams,containers
import importlib

def main(container_name):
    
    c = containers.query.filter(containers.name==container_name).first()

    if not c:
        return 'container_name %s not found'%container_name
    teams = Teams.query.get(c.teamid)
    #print c.to_json()
    s=c.typename
    #for s in subject:
    m = importlib.import_module('subject.'+s)
    try:
            # (self,typename, name,sshpassword, sshaccount, serviceport,sshport,teamid,score,ip='')
            # (self, teamid,teamname, sshport,serviceport,teampass,score)
            #  o(teamid,teamname, sshport,serviceport,teampass,score,ip,image)
        sj = m.o(c.teamid,'not use', c.sshport,c.serviceport,c.sshpassword,c.score,c.ip,s)
    except Exception,e:
        print e
        pass
    #sj = m.o()
    print sj

    sj.clear_container()
    sj.create_containers()
    sj.run()
    print container_name,'restart ok'
    return '%s -> %s restart ok'%(teams.name,container_name)






if __name__ == '__main__':
    container_name = (sys.argv[1])
    main(container_name)