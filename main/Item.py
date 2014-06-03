#coding:utf-8
'''
Created on 2014年4月15日

@author: admin
'''

 
# Initial all members into -1,
# Invoke isValid to detect if one of the member is not given.
class Item(object):
    
    def __init__(self):
        pass
    
    # initial all member into -1,
    def isValid(self):
        types = [type(i) for i in [0, "0", [0], {0:1}, (0,)]]  # list 5 basic types here.
        vals  = [i for i in ( -1, '-1', {}, () ) ]           # list expected empty values 
        for k in dir(self):  
            mem = eval("self.%s" % k)
            if type(mem) in types and mem in vals:  
                    return False
        return True

class FigureItem(Item):
    
    def __init__(self):
        super(FigureItem, self).__init__()
        
        self.uid        = -1
        self.domainid   = -1
        self.follow     = -1
        self.fans       = -1
        self.weibo      = -1
        self.establish  = -1     #better time stamp 
        self.name       = '-1'
        self.verify     = '-1'
        self.intro      = '-1'
        self.tags       = []
        
        
class WeiboItem(Item):

    def __init__(self):
        super(WeiboItem, self).__init__()
        #  mid, omid, thumbs, forwarding, comment, establish, text
        self.uid         = -1
        self.mid         = -1
        self.omid        = -1
        self.thumbs      = -1
        self.forwarding  = -1
        self.comments    = -1
        self.establish   = -1     #better time stamp
        self.text        = '-1' 
        
        
        
class CommentItem(Item):
    
    def __init__(self):
        super(CommentItem, self).__init__()
        
        self.uid      = -1
        self.mid      = -1
        self.cid      = -1
        self.comments = -1
        self.thumbs   = -1 
        self.text     = '-1'
        
        
        
class AnalyseItem(Item):
    
    def __init(self):
        super(AnalyseItem, self).__init__()
        self.id             = -1
        self.name           = '-1'
        self.establish      = -1
        self.weibos         = -1
        self.origin         = -1
        self.fans           = -1
        self.follow         = -1
        self.totalforwards  = -1
        self.totalcomments  = -1   
        self.HF             = -1
        self.HC             = -1