import sys
from batch import start_docker
from models import db,Teams,containers
import importlib

def main(container_name):


    teams = Teams.query.all()


    c = containers.query.filter(containers.name==container_name).first()
    print c.to_json()

    s=c.typename
    #for s in subject:
    m = importlib.import_module('subject.'+s)



    try:

        sj = m.o(c.teamid,'not use', c.sshport,c.serviceport,c.sshpassword,c.score)
    except:
        pass
    #sj = m.o()

    print sj


    sj.clear_container()
    sj.create_containers()
    sj.run()

    print container_name,'restart ok'

















if __name__ == '__main__':
    container_name = (sys.argv[1])
    main(container_name)