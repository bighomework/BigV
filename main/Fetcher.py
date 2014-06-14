#coding: utf-8

''' 

@author: admin
'''
import threading
import Queue
import re, json, time
from login import LoginFail
from pyquery import PyQuery
from Item import FigureItem, WeiboItem, CommentItem
from itemReader import Page, WeiboPage, CommentPage
from itemDatabase import Database, FigureDatabase, CommentDatabase, WeiboDatabase, FollowDatabase
import pickle
from os.path import exists

# a wrap of itemReader and itemDatabase
class Fetcher(threading.Thread):
    
    def __init__(self):
        super(Fetcher, self).__init__()          
        
    def run(self):
        pass

# e.g.        depricated
# fr         = FollowFetcher( 123456 )
# followlist = getFollowLst()
class FollowFetcher(Fetcher):
    
    def __init__(self):
        
        super(FollowFetcher, self).__init__() 
        self.localReader = FollowDatabase()
        self.remote      = Page()
        self.followLst = []
        self.pagenum = 0
        self.nextUrl = ''
        
    def getFollowLst(self, uid):
        self.uid = uid
        if not exists('../flist0.oj'):
            
            self.followLst = self._fetchlist(self.uid, self.followLst)
            flDict = dict(zip(self.followLst, [[]]))
            for fl in self.followLst:
                flDict[fl] = self.getLst(fl)
            with open('../flist0.oj', 'w') as f:
                pickle.dump(flDict, f)
        else:
            with open('../flist0.oj', 'r') as f:
                flDict = pickle.load(f)
                
        with open('../flist1.txt', 'w') as f:
            for one in flDict:
                f.write(one+' ')
                for i in flDict[one]:
                    f.write(i+' ')
                f.write('\n')
        return flDict

        
                
        #return self.followLst
        
    def getLst(self, uid):
        retLst = []
        self._fetchlist(self.remote.makeUrl_hostfollow(self.uid), retLst)    
        
    def _fetchlist(self, url, retLst):
        doc = self.remote.getDoc(url).decode('string_escape') 
        m = re.findall('<div class=\"name\">\s+(.*)\s+(.*)', doc)
        if m:
            for i in m: 
                #if re.search('class=\"W_ico16 approve\"', i[1]):
                userid = re.search('usercard=\"id=(\d+)\"', i[0]).group(1)
                retLst.append(userid)
                #else:
                    #continue 

        self.pagenum += 1
        if re.search(r'<span>下一页<\\/span><\\/a>', doc):
            url = self.remote.makeUrl_follow(self.uid, self.pagenum)
            if self.pagenum < 5:
                self._fetchlist(url, retLst)



# e.g.
# cr      = CommentFetcher( 123456 ) mid, uid is not required
# comment = cr.getCommentLst()
class CommentFetcher(Fetcher):
    
    def __init__(self):
        super(CommentFetcher, self).__init__()
        self.localReader = CommentDatabase() 
        self.nexturl = ''
        self.rawDoc  = ''
        self.uid = 2862441992           # none use
        
        
        self.cidmask = re.compile('object_id=(\d+)')
        self.uidmask = re.compile('id=(\d+)')
        self.nummask = re.compile('\((\d+)\)')
        
    # if database has records, never read the internet
    def run(self, mid):
        self.mid = mid  
        self.repeat = 0
        for doc in CommentPage(self.uid, self.mid):
            self.commentLst = []
            if self._parseComment(doc):
                break 
            self.localReader.record( self.commentLst )
        ret = self.localReader.fetchLst(self.mid)
        return ret
         
    
    def _parseComment(self, doc): 
        d = PyQuery(doc) 
        repeat = 0
        for c in d('dl.comment_list.S_line1').items():
            t = CommentItem()
            dd = c.children('dd')
            #print dd.children('div.info').children('a').eq(1).outerHtml()
            m = re.search(self.nummask, dd.children('div.info').children('a').eq(0).text())
            if m:
                t.thumbs = m.group(1)
            else:
                t.thumbs = 0
                
            m = re.search(self.nummask, dd.children('div.info').children('a').eq(1).text())
            if m:
                t.comments = m.group(1)
            else:
                t.comments = 0
                
            t.cid  = re.search(self.cidmask, 
                              dd.children('div.info').children('a').attr('action-data')
                              ).group(1)
            t.uid  = re.search(self.uidmask,
                              dd.children('a').attr('usercard')
                              ).group(1)
            t.mid  = self.mid
            
            text = dd.remove('a').remove('span').remove('div').text()
            if text:
                t.text = text[1:] 
                  
            # once you fetch a same comment, you say that there is no newer comments
            if self.localReader.fetch(t.cid):
                repeat += 1
            
            if t.isValid():
                self.commentLst.append(t)  
            else:
                print '_parsecomment: item not complete'  

            if repeat > 19:
                return True

 
 
# e.g. 
# wr     = WeiboFetcher( 123456 )
# html   = wr.run()   # return a list of WeiboItem object
class WeiboFetcher(threading.Thread):
    
    def __init__(self, queue=None, no=0, skip=False):         
  
        super(WeiboFetcher, self).__init__() 
        
        self.initRemask()
        self.remoteReader   = Page() 
        
        self.figure   = FigureItem()
        self.q = queue
        self.no = no
        self.repeat = 0
        self.skip = skip
        
        
        
    def initRemask(self):
        self.datamask = re.compile(u'(\(\d+\))?.*转发(\(\d+\))?.*评论(\(\d+\))?')
        self.midmask  = re.compile('mid=\"(\d+)\"')
        self.uidmask  = re.compile('ouid=(\d+)')  
        self.followmask = u'(\d+)\s*</strong>\s*<span>\s*关注\s*</span>'
        self.fansmask   = u'(\d+)\s*</strong>\s*<span>\s*粉丝\s*</span>'
        self.weibomask  = u'(\d+)\s*</strong>\s*<span>\s*微博\s*</span>'
        self.localReader    = WeiboDatabase()
        self.figureReader   = FigureDatabase()
        
    #for thread use
    def run(self):  
        self.localReader    = WeiboDatabase()
        self.figureReader   = FigureDatabase()
        while not self.q.empty():
            row = self.q.get() 
            if row:
                self.getWeibo( int(row), self.skip )
                print u'- Thread {0}: {1} items left.'.format(self.no, self.q.qsize())
            else:
                continue
            
    
         
    #for single use
    def getWeibo(self, uid, skip=False):
        self.uid = uid
        self.skip = skip
        print u'- Thread {0} Fetcher: start getting pages with uid = {1}'.format(self.no, self.uid)
        if not self.figureReader.fetch(self.uid):
            doc = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostweibo(self.uid) )
            fg = self._parseHeadinfo(doc)
            self.figureReader.record( fg )
            print u'- Thread {0} Fetcher: weibo figure {1} recorded.'.format(self.no, fg.uid)
        else:
            if self.skip:
                print u'- Thread {0} skipping..'.format(self.no)
                return False
            else:
                print u'- Thread {0} Fetcher: weibo figure {1} already recorded.'.format(self.no, self.uid)
            
        for doc in WeiboPage(self.uid, self.no): 
            try:
                self.weiboLst   = []
                if not self._parseWeibo(doc):
                    print u'- Thread {0} Fetcher: weibo already got.'.format(self.no)
                    break;
                self.localReader.recordLst(self.weiboLst)
            except:
                continue 
         
        return True
    
    def _parseWeibo(self, doc):
        d = PyQuery( doc )
        
        repeat = 0
        iterator = d('.WB_feed_type.SW_fun.S_line2').items()
        for i in iterator:
            t = WeiboItem()
            t.uid = re.search(self.uidmask, i.attr('tbinfo')).group(1)
            
            if i.attr('mid'):
                t.mid  = int(i.attr('mid'))
             
            if i.attr('omid'):
                t.omid = int(i.attr('omid'))
            else:
                t.omid = 0
                
 
            t.text = i('.WB_detail').find('.WB_text').text()
            text2 = i('.WB_media_expand.SW_fun2.S_line1.S_bg1').find('.WB_text').text()
            if text2:
                #print text2
                t.text = text2
                
            try:
                dat = i('.WB_detail').children('.WB_func.clearfix').children('.WB_from') \
                                     .children('a').attr('date')[:-4]
                t.establish = dat
            except:
                pass
            
                             
            form = i('.WB_detail').children('.WB_func.clearfix').text()
            if form:
                t.thumbs     = 0
                t.forwarding = 0
                t.comments   = 0
                m = re.search(self.datamask, form)
                if m:
                    if m.group(1):
                        t.thumbs        = int(m.group(1)[1:-1])
                    if m.group(2):
                        t.forwarding    = int(m.group(2)[1:-1])
                    if m.group(3):
                        t.comments      = int(m.group(3)[1:-1])
            
            if t.isValid():
                if self.localReader.fetch(t.mid):
                    repeat += 1
                else:
                    self.weiboLst.append(t)
            else:
                print '    - Thread {0} parseweiboinfo: item not complete, will be discard'.format(self.no)
            
            if repeat > 10: 
                return False
             
        return True

    def _parseHeadinfo(self, doc):
              
        fg = FigureItem()
        strimdata  = ''
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', doc)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print '_fetch_manload: raw doc parse error'
            
        for jdic in jdiclst:
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    strimdata = jdic['html']
                    d = PyQuery( strimdata ) 
                    break
        else:
            raise Exception('_parseHeadinfo error')
        
        
        info = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostinfo(self.uid) )
        m = re.search(r'注册时间[.\s\S]+(\d{4})-(\d{2})-(\d{2})', info) 
        if m:
            t = time.mktime(time.strptime('%s-%s-%s' % (m.group(1), m.group(2), m.group(3)), '%Y-%m-%d'))
        else:
            t = 0  #2012-07-06
        
        fg.uid       = self.uid
        fg.domainid  = self.remoteReader.domain
        fg.establish = t
        fg.follow = re.search(self.followmask, strimdata).group(1)
        fg.fans = re.search(self.fansmask, strimdata).group(1)
        fg.weibo = re.search(self.weibomask, strimdata).group(1)
        
        text1 = d('span').filter('.name').text()
        text2 = d('strong').filter('.W_f20.W_Yahei').text()
        if text1:
            fg.name = text1
        else:
            fg.name = text2
             
        try:
            fg.verify = d('.pf_verified_info').contents()[0]
        except:
            fg.verify = ''
            
            
        fg.intro = d('.pf_intro').text()
         
        for i in d('.layer_menulist_tags').items('a'):
            fg.tags.append( i.text() ) 
            
        if not fg.isValid():
            print '    - Thread {0} weibo figure info not enough'.format(self.no)
                
        else:
            return fg    
    
# e.g.
# fr = FigureFetcher( 123456 )
# fg = fr.getFigure()    # fg is a Figure object
class FigureFetcher(Fetcher):
    
    def __init__(self, queue):         
        super(FigureFetcher, self).__init__()
        self.localReader = FigureDatabase()
        self.figure = FigureItem() 
        
        self.q = queue
        
  
    def run(self):
        fg = FigureItem()
        while not self.q.empty():
            uid = int(self.q.get()[0])
            doc = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostweibo(uid) )
            self._parseHeadinfo(doc)
            self.remoteReader.finishFetching()
            self.localReader.record( fg ) 

    def _parseHeadinfo(self, doc):
          
        strimdata  = ''
        jdiclst = []
        scripts = re.findall('<script>FM\.view\((.*)\);?</script>', doc)
        if scripts:
            for i in scripts:
                jdiclst.append( json.loads(i) )
        else:
            print '_fetch_manload: raw doc parse error'
            
        for jdic in jdiclst:
            if 'ns' in jdic:
                if jdic['ns'] == 'pl.header.head.index':
                    strimdata = jdic['html']
                    d = PyQuery( strimdata ) 
                    break
        else:
            raise Exception('_parseHeadinfo error')
        
        
        info = self.remoteReader.getDoc( self.remoteReader.makeUrl_hostinfo(self.uid) )
        m = re.search(r'注册时间[.\s\S]+(\d{4})-(\d{2})-(\d{2})', info) 
        if m:
            t = time.mktime(time.strptime('%s-%s-%s' % (m.group(1), m.group(2), m.group(3)), '%Y-%m-%d'))
        else:
            t = 0  #2012-07-06
        
        self.figure.uid       = self.remoteReader.uid
        self.figure.domainid  = self.remoteReader.domain
        self.figure.establish = t
        self.figure.follow = re.search(self.followmask, strimdata).group(1)
        self.figure.fans = re.search(self.fansmask, strimdata).group(1)
        self.figure.weibo = re.search(self.weibomask, strimdata).group(1)
        
        text1 = d('span').filter('.name').text()
        text2 = d('strong').filter('.W_f20.W_Yahei').text()
        if text1:
            self.figure.name = text1
        else:
            self.figure.name = text2
             
        try:
            self.figure.verify = d('.pf_verified_info').contents()[0]
        except:
            self.figure.verify = ''
            
            
        self.figure.intro = d('.pf_intro').text()
         
        for i in d('.layer_menulist_tags').items('a'):
            self.figure.tags.append( i.text() ) 
            
        if not self.figure.isValid():
            print '    - Thread {0} weibo figure info not enough'.format(self.no)
                
                
                
                
                