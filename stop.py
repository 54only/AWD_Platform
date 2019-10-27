from dockercontr import clear_container
from models import db,Teams



def main():
    teams = containers.query.all()
    for i in teams:
        clear_container(i.name)    
        print(i.name,'removed')




if __name__ == "__main__":
    main()

    print('''# docker container prune && docker volume rm $(docker volume ls -qf dangling=true)''')

