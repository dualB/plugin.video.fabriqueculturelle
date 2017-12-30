#""" -*- coding: utf-8 -*- """
import copy, re,xbmc

def get_liste_ids(txt):
    import xml.etree.ElementTree as ET
    
    liste = re.compile('<li data-content-id="(\d+)"', re.DOTALL).findall(txt)
    return liste

def getCopy(item):
    return copy.deepcopy(item)

