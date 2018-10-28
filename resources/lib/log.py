# -*- coding: utf-8 -*-
# version 1.0.1 par dualB

import xbmcaddon, xbmc

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[ La Fabrique Culturelle ]: ' +msg)
        
def logjson(json):
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log(simplejson.dumps(json, sort_keys=True,indent=4, separators=(',', ': ')))

def loglist(liste):
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        message =''
        for item in liste:
            message=message+str(item)+'\n'
        xbmc.log(message)
