#coding:utf-8

'''
@author: admin
'''
import csv
from xml.sax.handler import ContentHandler  
from xml.sax import parse  
from xml.etree import ElementTree as ET
import pickle
import math
import re 
import os.path
import config
from Item import *
from itemDatabase import WeiboDatabase, FigureDatabase
from gensim import corpora, models, similarities
import jieba
import logging

class DicHandler(ContentHandler):
    
    def __init__(self):
        self.content = False
        self.dic = []         
    
    def startElement(self,name,attrs):  
        if name == 'content':
            self.content = True
          
    def endElement(self,name):  
        if name == 'content':
            self.content = False
          
    def characters(self,chars):  
        if self.content:
            applst = list(jieba.cut(chars))
            applst = self.rmShortWords(applst)
            self.dic.append( applst )

    def rmShortWords(self, applst):
        ret = []
        for i in applst:
            if len(i) > 1:
                ret.append(i)
        return ret
        



class Analyser(object):
    
    def __init__(self, filename):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        self.buildIndex(filename)
        
        self.buildWords()
        if not os.path.exists(config.DICPATH):
            self.buildDics() 
        

    
    # self.idlst   :  an id list.
    # self.anaDict :  {'class': set(ids) }
    def buildIndex(self, filename):
        ret = dict()
        self.idlst = []
        with open(filename, 'r') as f:
            data = csv.reader(f) 
            for line in data:
                l = len(line)
                if l == 1:
                    continue
                else:
                    self.idlst.append(line[0])
                    for k in range(1, l):
                        key = unicode(line[k].strip())
                        val = line[0] 
                        if key not in ret:  
                            ret[key] = set()
                        else:
                            ret[key].add(val)   
        self.anaDict =  ret
  



    # create self.word
    def buildWords(self): 

#         cutter = DicHandler()
#         with open(self.datas, 'r') as xmlfile:
#             parse(xmlfile, cutter)
#         with open(self.pickle, 'wb') as picfile:
#             pickle.dump(cutter.dic, picfile)
#         self.word = cutter.dic
        pass
    
    def buildDics(self):
        
        #generate a total dictionary for index purpose from self.word without affecting self.word
        dictionary = corpora.Dictionary(self.word)  

        #representation with wordid in dictionary of self.word
        corpus = [dictionary.doc2bow(text) for text in self.word]
        
        #initializing a model with a corpus, this doesn't affect corpus itself
        wvMdl = models.Word2Vec(self.word)
        
        # this [] is a transform operator
        retlst = wvMdl.most_similar(positive=[u'时尚'], topn=100 )
        for r in retlst:
            print r[0]
        
         
        pass
    
    
    def textClassify(self, uid):
        #word_vec = models.Word2Vec(self.wordDict)
        pass
    
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
    
    
    def printResult(self):
        self.textClassify(1501333927)
        pass
    
    def depre_printResult(self):
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
            
    
    
