# -*- coding: utf-8 -*-
from models import db,Teams,Flags
import time
import requests
from log import logger
#from flagfresher import service_down



def service_checker(mathobj):
    #获取当前最大的轮数
    #round_cont = db.session.query(func.max(Flags.rounds)).scalar()

    for i in mathobj:
        i.check_L1()
    db.session.commit()
    time.sleep(60)
    return
 


def main():
    return

        #break



if __name__ == '__main__':
    main()