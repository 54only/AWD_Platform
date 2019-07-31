<<<<<<< HEAD
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
=======
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
>>>>>>> 24f7ab02afd9b07609236db5546f84dd55656685
