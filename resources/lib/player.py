# -*- coding: utf8 -*-
# version 1.0.1 par dualB

import sys,urllib, xbmcgui, xbmcplugin, xbmcaddon,re,cache, xbmc, Item, simplejson

__handle__ = int(sys.argv[1])


def jouer_video(media_uid):
    """ function docstring """  
    show = Item.ItemVideo(media_uid)
    
    source = show['source']
    if source!='mnmedia':
        xbmc.executebuiltin('Notification(Source non supportée,Le source %s n''est pas supporté actuellement,,8000)' % simplejson.dumps(source))
        return

    m3u8_pl=m3u8(show['sourceId'])
    uri = obtenirMeilleurStream(m3u8_pl)   

    if uri:
        item = xbmcgui.ListItem(\
            show['nom'],\
            iconImage=show['image'],\
            thumbnailImage=show['fanart'], path=uri)

        play_item = xbmcgui.ListItem(path=uri)
        xbmcplugin.setResolvedUrl(__handle__,True, item)
    else:
        xbmc.executebuiltin('Notification(Aucun lien disponible,Incapable d''obtenir lien du vidéo,5000)')

def m3u8(refID):
    return cache.get_cached_content('https://mnmedias.api.telequebec.tv/m3u8/%s.m3u8' % refID,False)

def obtenirMeilleurStream(pl):
    """ function docstring """
    maxBW = 0
    bandWidth=None
    uri = None
    for line in pl.split('\n'):
        
        if re.search('#EXT-X',line):
            bandWidth=None
            try:
                match  = re.search('BANDWIDTH=(\d+)',line)
                bandWidth = int(match.group(1))
            except :
                bandWidth=None
        elif line.startswith('http'):
            if bandWidth!=None:
                if bandWidth>maxBW:
                    maxBW = bandWidth
                    uri = line
    return uri

