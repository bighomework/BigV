#coding: utf-8
'''
Created on 2014年4月11日

@author: admin
'''


def transformer():
    
    with open('../a.txt', 'r') as a:
        with open('../b.txt', 'w') as b:
            plain = a.read()
            unicodeText = plain.decode('unicode_escape')
            utf8Text = unicodeText.encode('utf-8')
            b.write(utf8Text)
            
            