#coding:utf-8
'''
Created on 2014年4月11日

@author: admin
'''
import re
import urllib2
import login
import config
import threading
from Queue import Queue

class Proxy(threading.Thread):
    
    def __init__(self, user, pwd, proxyip = False): 
        super(Proxy, self).__init__()
        login.Login(user, pwd, proxyip) 
     
    def run(self):
        while True:
            o = urllib2.urlopen('http://weibo.com')
            doc = o.read()
            assert( len(doc) > 300000 )
            print len(doc)

if __name__ == '__main__':
    proxy1 = 'http://27.50.30.50:80'
    proxy2 = 'http://14.102.111.185:80'
    proxy3 = 'http://42.121.105.191:80'
    proxy4 = 'http://14.29.117.38:80'
    p1 = Proxy(config.TEST_USER, config.TEST_PWD, proxy4)  
    p1.start()
    