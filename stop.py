from dockercontr import clear_container
from models import db,Teams



def main():
    teams = Teams.query.all()
    for i in teams:
        clear_container(i.teamcontainer)    
        print(i.teamcontainer,'removed')




if __name__ == "__main__":
    main()

    print('''# docker container prune
    # docker volume rm $(docker volume ls -qf dangling=true)''')

from dockercontr import clear_container
from models import db,Teams



def main():
    teams = Teams.query.all()
    for i in teams:
        clear_container(i.teamcontainer)    
        print(i.teamcontainer,'removed')




if __name__ == "__main__":
    main()

    print('''# docker container prune\n# docker volume rm $(docker volume ls -qf dangling=true)''')

