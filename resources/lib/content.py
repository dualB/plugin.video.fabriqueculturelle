# -*- coding: utf8 -*-
 
# version 1.0.0 - By CB

import urllib2, simplejson, parse, cache, re, xbmcaddon, html, xbmc,unicodedata, Item

BASE_API = 'http://api.lafabriqueculturelle.tv/v1/'
BASE_WEB = 'https://www.lafabriqueculturelle.tv'
BASE_SEARCH = BASE_WEB + '/content/load'

membreId='partenaireId'
themeId = 'themeId'
regionId = 'regionId'
form=  'format'
terme = 'terme'
motcle = 'motcle'
page= 'page'
pagesize='pagesize'
groupBy = 'groupBy'

exclureCommunauteOnly = 'exclureCommunauteOnly'
hasPublicite = 'hasPublicite'

def peupler(filtres):
    ajouterItemAuMenu(getContent(filtres))

def ajouterItemAuMenu(items):    
    for item in items:
        item.addVideo()

def getContent(filtres):
    if filtres['finished']==False:
        if filtres['groupBy']=='':
            return mainMenu()
        else:
            return menuGroupes(filtres)
    else:
        return get_liste(filtres)


def filtreVide():
    return {'finished':False,'groupBy':'','search':{membreId:'',themeId:'',regionId:'',form:'',terme:'',motcle:'',\
                                                    page:'1',pagesize:xbmcaddon.Addon().getSetting('nbRecherche'),\
                                                    exclureCommunauteOnly:True,hasPublicite:True}}


def mainMenu():  
    liste = []
    liste.append(Item.ItemDir("Naviguer par région",filtreVide(),regionId,True, BASE_API +'Regions',1))
    
    liste.append(Item.ItemDir("Naviguer par thème",filtreVide(),themeId, True, BASE_API +'Categories',1))

    liste.append( Item.ItemDir('Naviguer par partenaire',filtreVide(),membreId, True,BASE_API +'Partners',1))
    
    for item in getFormats():
        f = filtreVide()
        f['search'][form]=str(item['formatId'])
        f['finished'] = True
        liste.append(Item.ItemDir(item['title'],f,themeId,True, BASE_API,1))
    #liste.append(Item.ItemDir('Par format',filtreVide(),form, True,BASE_API +'Formats',1,\
    #                     xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'))

    liste.append(Item.ItemDir('Rechercher par mot-clé',filtreVide(),terme, True,BASE_SEARCH,10))
    
    return liste

def menuGroupes(filtres):

    gr = filtres[groupBy]
    
    liste = []

    if gr==regionId:
        for item in getRegions():
            f = parse.getCopy(filtres)
            f['search'][gr]=str(item[regionId])
            f['finished'] = True
            
            liste.append(Item.ItemDir(item['name'],f,regionId,True, BASE_API,1))

    elif gr==themeId:
        for item in getCategories():
            f = parse.getCopy(filtres)
            f['search'][gr]=str(item['categoryId'])
            f['finished'] = True
            liste.append(Item.ItemDir(item['title'],f,themeId,True, BASE_API,1))

    elif gr==form:
        for item in getFormats():
            f = parse.getCopy(filtres)
            f['search'][gr]=str(item['formatId'])
            f['finished'] = True
            liste.append(Item.ItemDir(item['title'],f,themeId,True, BASE_API,1))

    elif gr==membreId:
        for item in getPartners():
            f = parse.getCopy(filtres)
            f['search'][gr]=str(item['partnerId'])
            f['finished'] = True
            liste.append(Item.ItemDir(item['name'],f,themeId,True, BASE_API,1,\
                       getThumbnails(item['imageUrlTemplate']),getFanArt(item['imageUrlTemplate'])))
    elif gr=='serie':
        htmltxt = getCapsules(filtres['url'])
        listeId = parse.get_liste_ids(htmltxt)
        for item in listeId:
            ajouterUnItem(liste,item)
    elif gr=='dossier':
        listeId = getDossier(filtres['url'])
        for item in listeId:
            liste.append(Item.ItemVideo(item))
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

    pageActuelle = int(filtres['search']['page'])
    import math
    nbPages = int(math.ceil((nbItemsTotal*1.0)/nbItemsActuels))

    #if not pageActuelle==1:
    #    creerNavig(listeFiltree,filtres, 'Page précédente', pageActuelle-1,nbPages)

    for item in listeId:
        ajouterUnItem(listeFiltree,item)

    if not endOfList:
        creerNavig(listeFiltree,filtres, 'Page suivante', pageActuelle+1,nbPages,'/resources/media/fleche.png' )
        
    return listeFiltree

def creerNavig(liste,filtres, titre, numPage, totalPage,icon = '/icon.png'):
    filtre = parse.getCopy(filtres)
    filtre['search']['page'] =str(numPage)
    titre = "[B]"+titre+ " (" +  str(numPage) + " sur " + str(totalPage)+")[/B]"

    liste.append(Item.ItemDir(titre,filtre,filtre[groupBy],True, '',1,\
                   xbmcaddon.Addon().getAddonInfo('path')+icon,xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'))

def ajouterUnItem(liste, item):
    
    if parse.isSerie(item):
        mediaID = parse.getId(item)
        serie = getSerie(mediaID)       
        f = filtreVide()
        f['groupBy']='serie'
        f['url'] = serie['permalink']
        f['finished'] = False
        liste.append(Item.ItemDir(serie['title'],f,'serie',True, serie['permalink'],5,\
                       getThumbnails(serie['imageUrlTemplate']),getFanArt(serie['imageUrlTemplate']),serie['publishDate'],serie['description']))

        
    elif parse.isDossier(item):
        url = parse.getSerieUrl(item)
        title = html.html_unescape((parse.getTitle(item)).encode('utf-8','ignore'))
        image = 'http:'+parse.getImage(item)
        f = filtreVide()
        f['groupBy']='dossier'
        f['url'] = url
        f['finished'] = False
        liste.append(Item.ItemDir(title,f,'dossier',True, url,6,image))

    elif parse.isBalado(item):
        title = parse.getTitle(item)
        liste.append(Item.ItemDummy('[BALADO] '+title,'[BALADO] '+title))
    elif parse.isArticle(item):
        title = parse.getTitle(item)
        liste.append(Item.ItemDummy('[ARTICLE] '+ title,'[ARTICLE] '+title))        
    else:
        mediaID = parse.getId(item)
        liste.append(Item.ItemVideo(mediaID))
   
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

def getSerie(mediaId):
    database = simplejson.loads(cache.get_cached_content(BASE_API+ 'Containers/' + mediaId))
    return database

def getCapsules(url):
    return parse.getContents(cache.get_cached_content(url))

def getDossier(url):
    return parse.getDossiers(cache.get_cached_content(url))

def getSearch(data):
    data = dict((k, v) for k, v in data.iteritems() if v)
    #logjson(data)
    return simplejson.loads(html.get_url_txt(BASE_SEARCH,data))


def getRegions():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Regions'))
    return database


def getCategories():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Categories'))
    return database


def getFormats():
    return [{'formatId':1,'title':'Les vidéos'},\
            #{'formatId':2,'title':'Les articles'},\
            #{'formatId':3,'title':'Les balados'},\
            {'formatId':4,'title':'Les dossiers'},\
            {'formatId':5,'title':'Les séries'}]


def getPartners():
    database = simplejson.loads(cache.get_cached_content(BASE_API + 'Partners'))
    return database    


