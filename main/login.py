#!/usr/bin/env python
#coding=utf8
'''
Created on 2014��4��6��
@author: admin
'''
 
import urllib
import urllib2
import cookielib
import base64
import re
import json 
import rsa
import binascii


class LoginFail(Exception):
    pass

#implement this class then parse the weibo web page.
class Login(object):
    
    def __init__(self, username, password, proxyip = False):
        
        http_support   = urllib2.HTTPHandler
        cookie_support = urllib2.HTTPCookieProcessor( cookielib.LWPCookieJar() )
        proxy_support  = urllib2.ProxyHandler( {'http': proxyip} )
        
        if not proxyip:
            opener = urllib2.build_opener( http_support, cookie_support )
        else:
            opener = urllib2.build_opener( http_support, cookie_support, proxy_support )
            # This time, rather than install the OpenerDirector, we use it directly:
            #ipdoc = urllib2.urlopen('http://iframe.ip138.com/ic.asp').read().decode('gbk')
            #print re.search('\[(\d+\.\d+\.\d+\.\d+)\]', ipdoc).group(1)
        urllib2.install_opener(opener)
        
        self.parameters = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': 'TGVuZGZhdGluZyU0MHNpbmEuY29t',
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.5)',
            '_': '1362560902427'
        }
        
        self.postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': '',
            'vsnf': '1',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'rsakv': '',
            'sp': '',
            'encoding': 'UTF-8',
            'prelt': '27',
            'url': 'http://www.weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        self.login(username, password)

    def login(self, username, password):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        try:
            servertime, nonce, pubkey, rsakv = self.get_servertime()
        except:
            return
        self.postdata['servertime'] = servertime
        self.postdata['nonce'] = nonce
        self.postdata['rsakv'] = rsakv
        self.postdata['su'] = self.get_user(username)
        self.postdata['sp'] = self.get_pwd(password, servertime, nonce, pubkey)
        postdata = urllib.urlencode(self.postdata)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'}
    
        req = urllib2.Request(
            url=url,
            data=postdata,
            headers=headers
        )
        result = urllib2.urlopen(req)
        text = result.read()
        p  = re.compile('location\.replace\([\"|\'](.*?)[\"|\']\)')
        p2 = re.compile('\"result\":(\w+),')
        try:
            login_url = p.search(text).group(1)
            doc = urllib2.urlopen(login_url).read()
            if p2.search(doc).group(1) != 'true':
                raise LoginFail('False Login failed')
        except: 
            raise LoginFail('Bad Page login failed')
    
    def get_servertime(self):
        url = 'http://login.sina.com.cn/sso/prelogin.php?' + urllib.urlencode(self.parameters)
        data = urllib2.urlopen(url).read()
        p = re.compile('\((.*)\)')
        try:
            json_data = p.search(data).group(1)
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            pubkey = data['pubkey']
            rsakv = data['rsakv']
            return servertime, nonce, pubkey, rsakv
        except:
            print 'Get severtime error!'
            return None
          
    def get_pwd(self, pwd, servertime, nonce, pubkey):
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537) 
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd) 
        passwd = rsa.encrypt(message, key) 
        passwd = binascii.b2a_hex(passwd)  
        return passwd
    
    def get_user(self, username):
        username_ = urllib.quote(username)
        username = base64.encodestring(username_)[:-1]
        return username
    
    
if __name__ == '__main__': 
    Login('694435343@qq.com','rosewood2322')
