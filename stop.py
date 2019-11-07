
from models import containers
import docker
client = docker.from_env()

def main():
    teams = containers.query.all()
    for i in teams:
        c = client.containers.get(i.name)    
        c.stop()
        c.remove()
        print(i.name,'removed')




if __name__ == "__main__":
    main()

    print('''# echo y | docker container prune && docker volume rm $(docker volume ls -qf dangling=true)''')

