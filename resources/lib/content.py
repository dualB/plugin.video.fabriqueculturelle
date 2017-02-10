# -*- coding: cp1252 -*-

""" -*- coding: utf-8 -*- """
# version 3.0.0 - By CB

import urllib2, simplejson, parse, cache, re, xbmcaddon, html

BASE_API = 'http://api.lafabriqueculturelle.tv/v1/'
BASE_RSS = 'http://www.lafabriqueculturelle.tv/rss/'

BASE_LIMELIGHT = 'http://api.lafabriqueculturelle.tv/v1/Limelight/'

#AZ_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/Az'
#DOSSIERS_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/folders'
#POPULAIRE_URL = 'http://zonevideo.api.telequebec.tv/data/v1/[YourApiKey]/populars/'
#MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"finished":"false","filterBy":{},"groupBy":[],"mediaBundleId":-1,"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'



def menu(filtres):
    if filtres['finished']=="false":
        if len(filtres['groupBy'])==0:
            return mainMenu(filtres)
        else:
            return menuGroupes(filtres)
    else:
        return get_liste(filtres)


def mainMenu(filtres):  
    liste = []
    region = {'nom': "Par region", 'resume':"","filtres":parse.getCopy(filtres)}
    region['filtres']['groupBy'] = ["regionId"]
    region['isDir']= True
    region['nom']= urllib2.unquote(region['nom'])
    region['url'] = BASE_API +'Regions'
    region['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
    region['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    liste.append(region)

    categorie = {'nom': "Par categorie", 'resume':"","filtres":parse.getCopy(filtres)}
    categorie['filtres']['groupBy'] = ["categoryId"]
    categorie['isDir']= True
    categorie['nom']= urllib2.unquote(categorie['nom'])
    categorie['url'] = BASE_API +'Categories'
    categorie['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
    categorie['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    liste.append(categorie)

    #forma = {'nom': "Par format", 'resume':"","filtres":parse.getCopy(filtres)}
    #forma['filtres']['groupBy'] = ["formatId"]
    #forma['isDir']= True
    #forma['nom']= urllib2.unquote(forma['nom'])
    #forma['url'] = BASE_API +'Formats'
    #forma['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
    #forma['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    #liste.append(forma)

    #tout = {'nom': "Tout le contenu", 'resume':"","filtres":parse.getCopy(filtres)}
    #tout['filtres']['finished'] = 'true'
    #tout['isDir']= True
    #tout['nom']= urllib2.unquote(tout['nom'])
    #tout['url'] = BASE_API
    #tout['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
    #tout['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
    #liste.append(tout)

    return liste

def menuGroupes(filtres):

    groupBy = filtres['groupBy'][0]
    
    liste = []

    if groupBy=="regionId":
        for region in getRegions():
            liste.append({'groupBy': 'region-'+region['slug'], 'nom': 'Region - ' + region['name'],'resume':'region '})
    elif groupBy=="categoryId":
        for categorie in getCategories():
            liste.append({'groupBy': 'categorie-'+categorie['slug'], 'nom': 'Categorie - ' + categorie['title'],'resume':'categorie'})
    elif groupBy=="formatId":
        for formats in getFormats():
            liste.append({'groupBy': '', 'nom': 'Format - ' +  formats['title'],'resume':'format'})
        

    for item in liste :
        item['isDir']= True
        item['nom']= urllib2.unquote(item['nom'])
        item['url'] = BASE_API +'Regions'
        item['image']=xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
        item['filtres'] = parse.getCopy(filtres)
        item['filtres']['groupBy'].pop(0)
        item['filtres']['filterBy'][groupBy] = item['groupBy']
        if len(item['filtres']['groupBy'])==0:
            item['filtres']['finished'] = 'true'

    
    return liste

def get_liste(filtres):

    listeFiltree=[]
    if len(filtres['filterBy'])==0:
        pass
    else:
        for key in filtres['filterBy'].keys():
            value = filtres['filterBy'][key]
            import xml.etree.ElementTree as ET
            xml = ET.parse(getRSS(value))
	    count = 0
            for node in xml.iter('item'):
		count =count+1
                nom = node.find('title').text
                url = node.find('link').text
                item = {'nom':nom , 'resume':""}

                item['url'] = url
                
                item['fanart']=xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
                item['filtres'] = parse.getCopy(filtres)

                url2= url[:url.rfind('/')]
                url3 = url2[url2.rfind('/')+1:]
                episode = getShow(url3)
                
                mediaContent = episode['mediaContents'][0]

                item['filtres']['sourceId'] = url3
                item['sourceId'] = url3

                item['nom'] = episode['title']
                item['image']=getThumbnails(episode['imageUrlTemplate'])

                item['isDir'] = False
                #item['categoryType'] = episode['categoryType']
                item['url'] = episode['permalink']
                item['credits'] = episode['credits']
                item['genreId'] = ''
                item['nomComplet'] = episode['title']
                item['description'] = episode['shortDescription']
                item['resume'] =episode['description']
                #item[SEASON] = 'Saison ' + str(episode['seasonNo'])
                item['duree'] = 0 #episode['duration']/1000

                
                item['seasonNo'] = None # episode['seasonNo']
                item['episodeNo'] = None #episode['episodeNo']
                item['startDate'] = episode['publishDates']['start']
                item['endDate'] = episode['publishDates']['end']
                item['endDateTxt'] = ''


                #item['streamInfo'] = episode['streamInfo']

                #item['nomDuShow'] = mainShowName
                
                
                #item[EPISODE] = 'Episode ' + str(episode['episodeNo']).zfill(2)
                item['fanart'] = getFanArt(episode['imageUrlTemplate'])
                #item['nom'] = ''

            #for tag in filtres['fullNameItems']:
             #   newItem['nom'] = newItem['nom'] + newItem[tag] + ' - '

            #newItem['nom'] = newItem['nom'] + episode['view']['title']
            



                listeFiltree.append(item)
                if count>100:
		    return listeFiltree

    
    return listeFiltree


def formatListe(liste, filtres):
    newListe = []
    for item in liste:
        newItem = {}
        newItem['isDir'] = True
        newItem['nom'] = item['view']['title']
        newItem['mediaBundleId'] = item['mediaBundleId']
        newItem['url'] = MEDIA_BUNDLE_URL + str(item['mediaBundleId'])
        newItem['image'] = getThumbnails(item)
        newItem['genreId'] = ''
        newItem['nomComplet'] = item['view']['title']
        newItem['resume'] = item['view']['description']
        newItem['fanart'] = getFanArt(item)
        newItem['filtres'] = parse.getCopy(filtres)
        newItem['filtres']['content']['mediaBundleId'] = item['mediaBundleId']
        newListe.append(newItem)

    return newListe

def getListeOfVideo(mediaBundleId, filtres):
    show = getShow(mediaBundleId)
    fanart_url = getFanArt(show)
    mainShowName = show['view']['title']
    
    newListe = []
    for bloc in show['mediaGroups']:
        if bloc['label'] == None:
            nomBloc = 'Contenu'
        else:
            nomBloc = bloc['label']
        
        for episode in bloc['medias']:
            newItem = {}
            newItem['isDir'] = False
            newItem[LABEL] = nomBloc
            newItem['categoryType'] = episode['categoryType']
            newItem['url'] = episode['permalink']
            newItem['image'] = getThumbnails(episode)
            newItem['genreId'] = ''
            newItem['nomComplet'] = episode['view']['title']
            newItem['resume'] = episode['view']['description']
            newItem[SEASON] = 'Saison ' + str(episode['seasonNo'])
            newItem['duree'] = episode['duration']/1000

            newItem['seasonNo'] = episode['seasonNo']
            newItem['episodeNo'] =episode['episodeNo']
            newItem['startDate'] = episode['startDate']
            newItem['endDate'] = episode['endDate']
            newItem['endDateTxt'] = episode['view']['endDate']


            newItem['streamInfo'] = episode['streamInfo']

            newItem['nomDuShow'] = mainShowName
            
            newItem['sourceId'] = episode['streamInfo']['sourceId']
            newItem[EPISODE] = 'Episode ' + str(episode['episodeNo']).zfill(2)
            newItem['fanart'] = fanart_url
            newItem['nom'] = ''

            for tag in filtres['fullNameItems']:
                newItem['nom'] = newItem['nom'] + newItem[tag] + ' - '

            newItem['nom'] = newItem['nom'] + episode['view']['title']
            newListe.append(newItem)

    return newListe



def isGenre(genreValue, show):
    genres = show['genres']
    for genre in genres:
        if genre['genreId'] == genreValue:
            return True

    return False

def isIntegral(show):
    if show['categoryType']==INTEGRAL:
        return True
    else:
        return False

def getThumbnails(url):
    thumbLink = re.sub('{w}', '320', url)
    thumbLink = re.sub('{h}', '180', thumbLink)
    return 'http:'+thumbLink

def getFanArt(url):
    thumbLink = re.sub('{w}', '1280', url)
    thumbLink = re.sub('{h}', '720', thumbLink)
    return thumbLink

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

def getRSS(subtext):
    
    return (cache.get_cached_path(BASE_RSS + subtext + '.xml'))

    return database

def getRegions():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Regions'))
    return database

def getCategories():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Categories'))
    return database

def getFormats():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Formats'))
    return database


def getJsonBlock(url, block):
    try:
        dataBlock = simplejson.loads(cache.get_cached_content(url))
        dataBlock = dataBlock['data'][block]['items']
    except ValueError:
        dataBlock = []
    finally:
        return dataBlock


