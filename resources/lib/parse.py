#""" -*- coding: utf-8 -*- """
import copy, re,xbmc

def get_liste_ids(txt):
    
    liste = re.compile('<li (.+?)</li>', re.DOTALL).findall(txt)
    return liste

def getId(txt):
    
    return re.compile('data-content-id="(\d+)"', re.DOTALL).findall(txt)[0]

def getP(txt):
    try:
        return re.compile('<a(.+?)/a>', re.DOTALL).findall(txt)[0]
    except Exception:
        return ' error'

def isBalado(item):
    return re.search('/balados/',item) is not None

def isSerie(item):
    return re.search('/series/',item) is not None

def getSerieUrl(txt):
    return re.compile('<a href="(.+?)"', re.DOTALL).findall(txt)[0]

def getTitle(txt):
    return re.compile('<h3 class="carte-titre">(.+?)</h3>', re.DOTALL).findall(txt)[0]

def getImage(txt):
    return re.compile('<img src="(.+?)"', re.DOTALL).findall(txt)[1]

def isDossier(item):
    return search(item,'collection')

def search(item, text):
    aLink = getContent(item)
    result =  re.compile(text,re.DOTALL).findall(aLink)
    return len(result)>0

def getContent(txt):
    return re.compile('<a.+?class="(.+?)">',re.DOTALL).findall(txt)[0]

def getContents(txt):
    return re.compile('<ul class="slider">(.+?)</ul>',re.DOTALL).findall(txt)[0]

def getDossiers(txt):
    return re.compile('/capsules/(\d+)/',re.DOTALL).findall(txt)

def getCopy(item):
    return copy.deepcopy(item)

