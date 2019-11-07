# -*- coding: utf-8 -*-
#import time
import requests
from log import logger
#from flagfresher import service_down



def service_checker(mathobj):
    #获取当前最大的轮数
    #round_cont = db.session.query(func.max(Flags.rounds)).scalar()

    for i in mathobj:
        try:
            i.check_L1()
            #i.session.close()
            #print 'session removed'
        except Exception,e:
            print 'checker'
            print e
        #i.update_checkstat()
    #time.sleep(5)
    return
 


def main():
    return

        #break



if __name__ == '__main__':
    main()