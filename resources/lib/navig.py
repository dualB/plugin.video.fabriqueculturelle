# -*- coding: utf8 -*-

# version 1.0.0 - By CB

import sys,urllib, xbmcgui, xbmcplugin, xbmcaddon,re,cache, simplejson, xbmc, content, unicodedata

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'

__handle__ = int(sys.argv[1])



def ajouterItemAuMenu(items):    
    for item in items:
        if item['isDir'] == True:
            ajouterRepertoire(item)
            
        else:
            ajouterVideo(item)



def ajouterRepertoire(show):
    nom = show['nom']
    url = show['url']
    iconimage =show['image']
    resume = remove_any_html_tags(show['resume'])
    fanart = show['fanart']
    filtres = show['filtres']

    if resume=='':
        resume = urllib.unquote(ADDON.getAddonInfo('id')+' v.'+ADDON.getAddonInfo('version'))
    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
        resume = '[B]'+nom+'[/B][CR]'+urllib.unquote(resume)
    if iconimage=='':
        iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0]+"?url="+url+\
        "&mode=1"+\
        "&filters="+urllib.quote(simplejson.dumps(filtres))
  
    is_it_ok = True
    liz = xbmcgui.ListItem(nom,iconImage=iconimage,thumbnailImage=iconimage)

    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title": nom,\
            "plot":resume
        }\
    )
    setFanart(liz,fanart)
    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

    return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)


def ajouterVideo(show):
    name = show['nom']
    the_url = show['url']
    iconimage = show['image']
    url_info = 'none'
    finDisponibilite = show['endDateTxt']

    resume = remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
    duree = show['duree']
    fanart = show['fanart']
    sourceId = show['sourceId']
    annee = show['startDate'][:4]
    premiere = show['startDate']
    episode = show['episodeNo']
    saison = show['seasonNo']

    mediaId = show['mediaId']
    


    is_it_ok = True

    entry_url = sys.argv[0]+"?url="+normalizeUrl(the_url)+"&sourceId="+str(mediaId)
    

    if resume != '':
        if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
            resume = '[B]'+name.lstrip()+'[/B]'+'[CR]'+resume.lstrip() 
    else:
        resume = name.lstrip()

    liz = xbmcgui.ListItem(\
        remove_any_html_tags(name), iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=iconimage)
    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title":remove_any_html_tags(name),\
            "Plot":remove_any_html_tags(resume, False),\
            "Duration":duree,\
            "Year":annee,\
            "Premiered":premiere,\
            "Episode":episode,\
            "Season":saison}\
    )
    liz.addContextMenuItems([('Informations', 'Action(Info)')])

    setFanart(liz,fanart)

    liz.setProperty('IsPlayable', 'true')

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
    return is_it_ok

RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')


def jouer_video(media_uid):
    """ function docstring """    
    show = content.formatShow(media_uid)
    
    source = show['source']
    if source!='mnmedia':
        xbmc.executebuiltin('Notification(Source non supportée,Le source %s n''est pas supporté actuellement,,8000)' % simplejson.dumps(source))
        return
        
    check_for_internet_connection()
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
    return cache.get_cached_content('https://mnmedias.api.telequebec.tv/m3u8/%s.m3u8' % refID)

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


def check_for_internet_connection():
    """ function docstring """
    if ADDON.getSetting('NetworkDetection') == 'false':
        return
   #retire cb
    
   # if html.is_network_available(parseTQ.BASE_URL) == False:
   #     xbmcgui.Dialog().ok(\
   #         ADDON_NAME,\
   #         ADDON.getLocalizedString(32112),\
   #         ADDON.getLocalizedString(32113)\
   #     )
   #     exit()
    return
def normalizeUrl(the_url):
    try:
        the_url =  unicodedata.normalize("NFKD", the_url)
        return urllib.quote_plus(the_url)
    except Exception:
        return the_url

def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    try:
        text = RE_HTML_TAGS.sub('', text)
        text = text.lstrip()
        if crlf == True:
            text = RE_AFTER_CR.sub('', text)
        return text
    except Exception:
        return ''

