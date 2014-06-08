#coding: utf-8
'''
@author: prehawk

'''

import time
import sys
import re
import os 
import config
import Queue
import csv
import getpass
from login import Login
from pyquery import PyQuery
from Item import FigureItem
from Fetcher import WeiboFetcher, FigureFetcher, CommentFetcher, FollowReader
from Analyser import Analyser

 
    
class Controller(object):
    
    def __init__(self):
        pass
        
    #single fetch
    def start_fetch_single(self, uid, username, password):
        Login(username, password, config.TEST_PROXY)
        WeiboFetcher().getWeibo(uid)
        
    
    #data flows to database
    def start_fetch(self, filename, username, password):
        Login(username, password, config.TEST_PROXY)
        
        q = Queue.Queue(100) 
        with open(filename, 'rb') as csvfile: 
            data = csv.reader(csvfile)
            for row in data: 
                q.put(row)
                
        for i in range(config.THREAD_N):
            WeiboFetcher(q, i).start()
            time.sleep(config.SPAWN_GAP)
         
    
    #using database
    def start_analyse(self, filename):
        a = Analyser(filename)
        a.printResult()
    
    
    
    
    def test_arg(self):
        a = '1234556666'
        b = '123455'
        
        print a[len(b):]
        
        
        
class Tester(Controller):
    
    def __init__(self):
        super(Tester, self).__init__()

    def test_printweibo(self):
        w = WeiboFetcher()
        wf = w.run(2862441992)
        for i in wf:
            print i.text
        
    def test_printfigure(self):
        f = FigureFetcher()
        fg = f.getFigure(2862441992)
        print fg.name
        
    def test_printcomment(self):
        c = CommentFetcher()
        cm = c.getCommentLst(3694134789199108)
        for c in cm:
            print c.text
     
    def debug_html(self):
        with open('../a.html', 'r') as f:
            d = PyQuery( f.read().decode('utf-8') )
        print d('.WB_detail').html()
        
    def test_getlotsfigure(self): 
        figure  = FigureFetcher()
        weibo   = WeiboFetcher()
        comment = CommentFetcher()
        with open('../followlist', 'r') as f:
            for line in f.readlines(): 
                figure.getFigure( int(line) )
                ret2 = weibo.run( int(line) )
                for r in ret2:
                    comment.getCommentLst(r.mid)
                break
                
                
    def test_nonetype(self):
        
        pass
    
    def test_re(self):
        text = u'| 转发(361) | 收藏| 评论(5) 2013-8-23 15:48 来自 微博 weibo.com | 举报'
        mask = re.compile(u'(\((\d+)\))?\|\s*转发\s*(\((\d+)\))?\s*\|\s*收藏\s*(\((\d+)\))?\|\s*评论(\((\d+)\))?')
        m = re.search(mask, text) 
        if m:
            print m.group(2)
            print m.group(4)
            print m.group(8)
        
        
    def test_parseWeiboLst(self, uid):
        fd = '../BigVs/' + str(uid)
        if os.path.exists(fd): 
            with open( '../BigVs/' + str(uid), 'r' ) as f:
                rawdoc = f.read()
            
            d = PyQuery( rawdoc.decode('utf-8') ) 
            fg = FigureItem()
            
            fg.follow = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'follow').text()
            fg.fans = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'fans').text()
            fg.weibo = d('strong').filter(lambda i, this: PyQuery(this).attr('node-type') == 'weibo').text()
            
            fg.name = d('span').filter('.name').text()
            fg.verify = d('.pf_verified_info').contents()[0]
            fg.intro = d('.pf_intro').text()
             
            for i in d('.layer_menulist_tags').items('a'):
                fg.tags.append( i.text() ) 
                
                
            return fg
        else:
            print 'file not exists'
        
    def test_writeWeiboLst(self, uid):

        wr = WeiboFetcher(uid)
        ret = wr.getWeiboHtml()
        
        
        savedir = '../BigVs/'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
            
        with open( savedir + str(ret[0]), 'w' ) as f:
            f.write(ret[1].encode('utf-8') + '\n\n')
            f.write(ret[2].encode('utf-8') )
    
    def test_writeFollowLst(self):
         
        followSet = set()
        with open('../followlist', 'r') as f: 
            for line in f.readlines():
                followSet.add( line ) 
 
        layerSet = followSet
        for uid in layerSet:
            
            newSet = set( FollowReader(uid).getFollowLst() )
            writeSet = newSet - followSet
            followSet.union(newSet)  
        
            with open('../followlist', 'a') as f:
                for w in writeSet:
                    f.write(w + '\n')




if __name__ == '__main__':
    c = Controller()
    if len(sys.argv) == 1:
        print 'Usage: python collector.py [fetch <filename> | analyse <filename>]'
    else:
        if sys.argv[1] == 'fetch' and len(sys.argv) == 3:
            username = raw_input('Input username: ')
            if not username:
                if unicode(sys.argv[2]).isnumeric():
                    print 'Collector: start fetching {0}.(using default accout)'.format(sys.argv[2])
                    c.start_fetch_single(sys.argv[2], config.TEST_USER, config.TEST_PWD)
                else:
                    print 'Collector: start fetching data.(using default accout)'
                    c.start_fetch(sys.argv[2], config.TEST_USER, config.TEST_PWD)
            else: 
                password = getpass.getpass('Input password: ')
                print 'Collector: start fetching data.(using specific accout)'
                c.start_fetch(sys.argv[2], username, password)   
                
        elif sys.argv[1] == 'analyse' :
            if len(sys.argv) == 3:
                print 'Collector: start analysing with database.'
                c.start_analyse(sys.argv[2])
                pass
            else:
                print 'Collector: need analyse file'
        else:
            print 'Unknown option!'
            
            
            
