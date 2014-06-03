#coding:utf-8

'''
@author: admin
'''
import csv
import math
import re 
from Item import *
from itemDatabase import WeiboDatabase, FigureDatabase
from gensim import corpora, models, similarities

class Analyser(object):
    
    def __init__(self, filename):
        self.anaLst = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.anaLst.append( line ) 

    
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration()
    
    def countHF(self, wbLst):
        wbLst.sort(cmp=lambda x,y: cmp(x.forwarding, y.forwarding), reverse=True)
        for no, i in enumerate(wbLst):
            if no >= i.forwarding:
                return no
    
    def countHC(self, wbLst):
        wbLst.sort(cmp=lambda x,y: cmp(x.comments, y.comments), reverse=True)
        for no, i in enumerate(wbLst):
            if no >= i.comments:
                return no
    
    def prepareData(self):
        Ana = []
        weibodata = WeiboDatabase()
        figuredata = FigureDatabase()
        for no, figure in enumerate(self.anaLst):
            f = figuredata.fetch(figure)
            wbLst = weibodata.fetchLst(figure)
            
            a = AnalyseItem()
            a.id             = no
            a.name           = f.name
            a.establish      = f.establish
            a.weibos         = len(wbLst)
            a.origin         = 0
            a.fans           = int(f.fans)
            a.follow         = int(f.follow)
            a.totalcomments  = 0
            a.totalforwards  = 0
            for i in wbLst:
                if i.omid:
                    a.origin += 1
                a.totalcomments += i.comments
                a.totalforwards += i.forwarding
            
            a.HF             = self.countHF(wbLst)
            a.HC             = self.countHC(wbLst)
            a.HM             = a.HF * 0.5 + a.HC * 0.5
            a.HM2            = a.HF ** 0.5 + a.HC ** 0.5
            
            if a.isValid():
                print '%s: weibo: %d, origin: %d, follows: %d, fans: %d, totoalfor: %d, totalcom: %d, HM: %d' \
                        % (f.name, a.weibos, a.origin, int(f.follow), int(f.fans), a.totalforwards, a.totalcomments, 
                           a.HM)
                Ana.append(a)
            else:
                print a
        Ana.sort(cmp=lambda x,y: cmp(x.HM2, y.HM2), reverse=True )
        print u'微博热度排名：'
        for no, i in enumerate(Ana):
            print no+1, i.name
            
    
    
