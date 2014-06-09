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
from os.path import exists
import config
from Item import *
from itemDatabase import WeiboDatabase, FigureDatabase
from gensim import corpora, models, similarities
import jieba
import logging
import time

class DicHandler(ContentHandler):
    
    def __init__(self):
        self.content = False
        self.class_dic = []         
    
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
            self.class_dic.append( applst )

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
        if not exists(config.CLASS_DIC) or exists(config.WORD_DIC):
            self.buildWords() 
            self.buildDics() 
        else:
            with open(config.CLASS_DIC, 'rb') as pfile:
                self.class_dic = pickle.load(pfile)
            self.word_dic = corpora.Dictionary()
            self.word_dic.load(config.WORD_DIC)
            
                
        

    
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

        weiboDB = WeiboDatabase() 
        self.sentences = []
        for uid in self.idlst:
            print '*FETCHING* id {0}'.format(uid)
            t = time.time()
            self.sentences.extend( [ [word for word in list(jieba.cut(weibo[0])) if len(word) > 1]\
                               for weibo in weiboDB.fetchText(uid)] )
            print 'extend to {0} weibos, using {1} secs!'.format(len(self.sentences), time.time()-t)
            #sreturn
        
            
    
    def buildDics(self):

        self.class_dic = dict()
        wvMdl = models.Word2Vec(self.sentences)
         
        for figure_class in self.anaDict.viewkeys():
            print '*BUILDING* {0} class_dic...'.format(figure_class)
            t = time.time()
            self.class_dic[figure_class] = [r[0] for r in wvMdl.most_similar(positive=[figure_class], topn=100 ) ]
            print 'Build complete using {0} secs!'.format(time.time()-t)
         
        with open(config.CLASS_DIC, 'wb') as picklefile:
            pickle.dump(self.class_dic, picklefile)
        
        self.word_dic = corpora.Dictionary(self.sentences)
        self.word_dic.save(config.WORD_DIC)
    
    
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
            
    
    
