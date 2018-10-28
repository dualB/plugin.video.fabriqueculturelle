# -*- coding: utf-8 -*-

# version 1.0.1 - By dualB

import os, urllib, sys, traceback, xbmcplugin, xbmcaddon, xbmc, simplejson, xbmcgui

from resources.lib import parse, content, player

def search():
    keyboard = xbmc.Keyboard('', 'Rechercher dans la Fabrique Culturelle ')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText()
        filtres['search']['terme']=search_string
        filtres['finished']=True
        content.peupler(filtres)
    
def get_params():
    """ function docstring """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for k in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[k].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def set_content(content):
    """ function docstring """
    xbmcplugin.setContent(int(sys.argv[1]), content)
    return

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))

PARAMS = get_params()

URL = None
MODE = None
SOURCE_ID = ''
FILTERS = ''
filtres = {}

try:
    URL = urllib.unquote_plus(PARAMS["url"])
    log("PARAMS['url']:"+URL)
except StandardError:
    pass
try:
    MODE = int(PARAMS["mode"])
    log("PARAMS['mode']:"+str(MODE))
except StandardError:
    pass
try:
    FILTERS = urllib.unquote_plus(PARAMS["filters"])
    filtres = simplejson.loads(FILTERS)
    filtres['search']['pagesize']=xbmcaddon.Addon().getSetting('nbRecherche')
except StandardError:
    filtres = content.filtreVide()
try:
    SOURCE_ID = urllib.unquote_plus(PARAMS["sourceId"])
except StandardError:
    pass
   
if SOURCE_ID !='':
    player.jouer_video(SOURCE_ID)

elif MODE == 99:
    ADDON.openSettings()
    
else:
    content.peupler(filtres)
    set_content('Videos')

if MODE is 10:
    search()
    
if MODE is not 99:
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if MODE is not 4 and xbmcaddon.Addon().getSetting('DeleteTempFiFilesEnabled') == 'true':
    PATH = xbmc.translatePath('special://temp')
    FILENAMES = next(os.walk(PATH))[2]
    for i in FILENAMES:
        if ".fi" in i:
            os.remove(os.path.join(PATH, i))
