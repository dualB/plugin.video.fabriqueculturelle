# -*- coding: utf8 -*-
 
# version 1.0.0 - By CB

import urllib2, simplejson, parse, cache, re, xbmcaddon, html, xbmc

BASE_API = 'http://api.lafabriqueculturelle.tv/v1/'
BASE_WEB = 'https://www.lafabriqueculturelle.tv'
BASE_SEARCH = BASE_WEB + '/content/load'

####
# Le lien à trouver est "      var referenceId = '36387';
# Puis sur https://mnmedias.api.telequebec.tv/m3u8/369387.m3u8
####

membreId='membreId'
themeId = 'themeId'
regionId = 'regionId'
form=  'format'
terme = 'terme'
motcle = 'motcle'
page= 'page'
pagesize='pagesize'
groupBy = 'groupBy'

#                    exclureCommunauteOnly: exclureCommunauteOnly,
#                    hasPublicite: hasPublicite


def getContent(filtres):
    if filtres['finished']==False:
        if filtres['groupBy']=='':
            return mainMenu()
        else:
            return menuGroupes(filtres)
    else:
        return get_liste(filtres)


def filtreVide():
    return {'finished':False,'groupBy':'','search':{membreId:'',themeId:'',regionId:'',form:'',terme:'',motcle:'',page:'1',pagesize:xbmcaddon.Addon().getSetting('nbRecherche')
}}


def creerItem(liste,nom,filtres,group,isDir,url,image,fanart):
    item = {'nom': urllib2.unquote(nom),'resume':'',"filtres":filtres,'isDir':isDir,'url':url,'image':image,'fanart':fanart}
    item['filtres'][groupBy] = group
    liste.append(item)


def mainMenu():  
    liste = []
    creerItem(liste,"Par région",filtreVide(),regionId,True, BASE_API +'Regions',\
                       xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg')
    
    creerItem(liste,"Par thème",filtreVide(),themeId, True, BASE_API +'Categories',\
                          xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg')

    creerItem(liste,'Par partenaire',filtreVide(),membreId, True,BASE_API +'Partners',\
                         xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg')

    creerItem(liste,'Par format',filtreVide(),form, True,BASE_API +'Formats',\
                         xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg')

    creerItem(liste,'Rerchercher un mot-clé',filtreVide(),terme, True,BASE_SEARCH,\
                         xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg')
    
    return liste

def menuGroupes(filtres):

    gr = filtres[groupBy]
    
    liste = []

    if gr==regionId:
        for item in getRegions():
            liste.append({'id':item['regionId'],'groupBy': 'region-'+str(item['friendlyUrl']), 'nom': item['name'],'resume':'Region'})
    elif gr==themeId:
        for item in getCategories():
            liste.append({'id':item['categoryId'],'groupBy': 'categorie-'+str(item['friendlyUrl']), 'nom': item['title'],'resume':'Theme'})
    elif gr==form:
        for item in getFormats():
            liste.append({'id':item['formatId'],'groupBy': 'theme-'+str(item['friendlyUrl']), 'nom': item['title'],'resume':'Format'})
    elif gr==membreId:
        for item in getPartners():
            liste.append({'id':item['partnerId'],'groupBy': 'theme-'+str(item['friendlyUrl']), 'nom': item['name'],'resume':item['description'],\
                          'image':getThumbnails(item['imageUrlTemplate'])})
    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        item['resume']= urllib2.unquote(item['resume'])
        item['url'] = BASE_SEARCH
        if not 'image' in item:
            item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres'] = parse.getCopy(filtres)
        item['filtres']['search'][gr]=str(item['id'])
        item['filtres']['finished'] = True
    
    return liste

def logjson(json):
    xbmc.log(simplejson.dumps(json, sort_keys=True,indent=4, separators=(',', ': ')))

def loglist(liste):
    message =''
    for item in liste:
        message=message+str(item)+'\n'
    xbmc.log(message)

def get_liste(filtres):

    listeFiltree=[]

    searchJson = getSearch(filtres['search'])
    
    if searchJson is None:
        xbmc.executebuiltin('Notification(Recherche indisponible,Incapable d\'obtenir un requête pour le contenu recherché %s,8000)' % value)
        return listeFiltree

    htmltxt =searchJson['html']

    listeId = parse.get_liste_ids(htmltxt)
    if len(listeId)==0:
        return listeFiltree
    nbItemsTotal = searchJson['count']
    endOfList = searchJson['endOfList']
    nbItemsActuels = len(listeId)

   # xbmc.log(str(nbItemsTotal) + ' ' + str(endOfList) + ' ' + str(nbItemsActuels))
    pageActuelle = int(filtres['search']['page'])
    import math
    nbPages = int(math.ceil((nbItemsTotal*1.0)/nbItemsActuels))

    if not pageActuelle==1:
        creerNavig(listeFiltree,filtres, 'Page précédente', pageActuelle-1,nbPages)

    for item in listeId:
        show = formatShow(item)
        show['filtres'] = parse.getCopy(filtres)
        listeFiltree.append(show)

    if not endOfList:
        creerNavig(listeFiltree,filtres, 'Page suivante', pageActuelle+1,nbPages)
        
    return listeFiltree

def creerNavig(liste,filtres, titre, numPage, totalPage):
    filtre = parse.getCopy(filtres)
    filtre['search']['page'] =str(numPage)
    titre = "[B]"+titre+ " (" +  str(numPage) + " sur " + str(totalPage)+")[/B]"

    creerItem(liste,titre,filtre,filtre[groupBy],True, '',\
                   xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg')


def formatShow(mediaID):
    episode = getShow(str(mediaID))
    
    item = {'nom': episode['title'], 'resume':episode['description']}
    item['mediaId'] = mediaID
    item['sourceId'] = episode['mediaContents'][0]['sourceId']
    item['source']=  episode['mediaContents'][0]['source']
    item['isDir'] = False
    item['url'] = episode['permalink']
    item['credits'] = episode['credits']
    item['image']=getThumbnails(episode['imageUrlTemplate'])
    item['fanart'] = getFanArt(episode['imageUrlTemplate'])
    try:
        item['genreId'] =  episode['categories'][0]['category']['title']
    except Exception:
        item['genreId'] = ''
    item['nomComplet'] = episode['title']
    item['description'] = episode['shortDescription']
    item['duree'] = 0 #episode['duration']/1000
    item['seasonNo'] = None # episode['seasonNo']
    item['episodeNo'] = None #episode['episodeNo']
    item['startDate'] = episode['publishDates']['start']
    item['endDate'] = episode['publishDates']['end']
    item['endDateTxt'] = str(item['endDate'])

    #item['nom'] = item['nom'] + ' ' + item['genreId'] + ' ' + item['mediaId']
    #item['nom'] = episode['title'] + ' ' + episode['mediaContents'][0]['sourceId'] +' ' + episode['region']['name'] + ' ' +episode['mediaContents'][0]['source']
    
    return item

def getThumbnails(url):
    thumbLink = re.sub('{w}', '320', url)
    thumbLink = re.sub('{h}', '180', thumbLink)
    return 'http:'+thumbLink

def getFanArt(url):
    thumbLink = re.sub('{w}', '1280', url)
    thumbLink = re.sub('{h}', '720', thumbLink)
    return 'http:'+ thumbLink

def getShow(mediaId):
    database = simplejson.loads(cache.get_cached_content(BASE_API+ 'Capsules/' + mediaId))
    return database

def getMediaUID(subtext):
    dictionnary = simplejson.loads((cache.get_cached_content(BASE_LIMELIGHT + subtext)))
    if dictionnary!=None:
        return dictionnary['limelightUid']
    return ''
    
    
def getAll():
    import xml.etree.ElementTree as ET
    database = ET.parse(cache.get_cached_content(BASE_RSS + 'capsules.xml'))
    return database


def getSearch(data):
    data = dict((k, v) for k, v in data.iteritems() if v)
    logjson(data)
    return simplejson.loads(html.get_url_txt_post(BASE_SEARCH,data))


def getRegions():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Regions'))
    return database


def getCategories():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Categories'))
    return database


def getFormats():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Formats'))
    return database


def getPartners():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Partners'))
    return database    

def getJsonBlock(url, block):
    try:
        dataBlock = simplejson.loads(html.get_url_txt(url))
        dataBlock = dataBlock['data'][block]['items']
    except ValueError:
        dataBlock = []
    finally:
        return dataBlock


