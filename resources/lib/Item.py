import content,  xbmcgui,xbmc,sys,html,xbmcplugin,parse,urllib2,urllib,xbmcaddon,simplejson

# version 1.0.0 - By CB

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/'
ADDON_THUMBNAIL = ADDON_IMAGES_BASEPATH+'logo.png'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'

try:
    youtube = xbmcaddon.Addon('plugin.video.youtube')
except Exception:
    youtube = None

try:
    vimeo = xbmcaddon.Addon('plugin.video.vimeo')
except Exception:
    vimeo = None

__handle__ = int(sys.argv[1])


class AutoFormatDict:
    item = None
    def __init__(self):
        self.item = {}
    def __getitem__(self, key):
        return self.item[key]
    def __setitem__(self,key,value):
        self.item[key] = value


class ItemDir:
        
    def __init__(self,nom,filtres,group,isDir,url,mode,\
                 image=ADDON_THUMBNAIL,fanart=ADDON_FANART,\
                 startDate=None,resume=''):
        self.item = AutoFormatDict()
        self.item['nom'] =nom
        self.item['resume']= resume
        self.item["filtres"]=filtres
        self.item['isDir']=isDir
        self.item['url']=url
        self.item['image']=image
        self.item['fanart']=fanart
        self.item['mode' ]=mode
        self.item['startDate']=startDate
        self.item['filtres']['groupBy'] = group
    def addVideo(self):
        show = self.item
        nom = show['nom']
        url = show['url']
        iconimage =show['image']
        resume = html.remove_any_html_tags(show['resume'])
        fanart = show['fanart']
        filtres = show['filtres']
        mode = show['mode']
        
        startDate = show['startDate']
        plot = show['resume']
        
        if iconimage=='':
            iconimage = ADDON_THUMBNAIL

        entry_url = sys.argv[0]+"?url="+url+\
            "&mode="+str(mode)+\
            "&filters="+urllib.quote(simplejson.dumps(filtres))
        is_it_ok = True
        liz = xbmcgui.ListItem(nom,iconImage=iconimage,thumbnailImage=iconimage)
        if startDate is not None:
            liz.setInfo(\
            type="Video",\
            infoLabels={\
                "Title":html.remove_any_html_tags(nom),\
                "Plot":html.html_unescape(html.remove_any_html_tags(plot,False)),\
                "Year":startDate[:4],\
                "Premiered":startDate}\

        )
        setFanart(liz,fanart)
        is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

        return is_it_ok


class ItemVideo:

    def __init__(self,mediaID,moreTitle = ''):
        episode = content.getShow(str(mediaID))
        title = moreTitle+episode['title']
        if episode['subTitle'] is not None:
            title = title +' | [I]' + episode['subTitle']+'[/I]'
        self.item = AutoFormatDict()
        self.item['nom']= title
        try:
            self.item['credits'] = html.clean(episode['credits'])
        except Exception:
            self.item['credits'] = ''
        
        self.item['shortPlot']= html.clean(episode['shortDescription'])
        self.item['longPlot'] = html.clean(episode['description'])+'\n'+ self.item['credits']
        self.item['mediaId'] = mediaID
        self.item['sourceId'] = episode['mediaContents'][0]['sourceId']
        self.item['source']=  episode['mediaContents'][0]['source']
        self.item['isDir'] = False
        self.item['url'] = episode['permalink']

        self.item['image']=content.getThumbnails(episode['imageUrlTemplate'])
        self.item['fanart'] = content.getFanArt(episode['imageUrlTemplate'])
        try:
            self.item['genreId'] =  episode['categories'][0]['category']['title']
        except Exception:
            self.item['genreId'] = ''
        self.item['nomComplet'] = episode['title']
        self.item['duree'] = 0 #impossible a connaitre
        self.item['startDate'] = episode['publishDates']['start']
        self.item['endDate'] = episode['publishDates']['end']
        self.item['endDateTxt'] = str(episode['publishDates']['end'])

    def __getitem__(self, key):
        return self.item[key]

    def addVideo(self):
        item = self.item
        name = item['nom']
        the_url = item['url']
        iconimage = item['image']
        url_info = 'none'
        finDisponibilite = item['endDateTxt']

        
        duree = item['duree']
        fanart = item['fanart']
        source = item['source']
        sourceId = item['sourceId']
        annee = item['startDate'][:4]
        premiere = item['startDate']
        shortPlot = item['shortPlot']
        longPlot = item['longPlot']
        mediaId = item['mediaId']
        credit = item['credits']
        
        is_it_ok = True

        nameFormatted = name
        
        if source == 'youtube' and youtube !=None:
            #nameFormatted = '[COLOR green]'+name+'[/COLOR]'
            entry_url = 'plugin://plugin.video.youtube/play/?video_id=%s' % str(sourceId)
        elif source == 'vimeo' and vimeo !=None:
            #nameFormatted = '[COLOR yellow]'+name+'[/COLOR]'
            entry_url = 'plugin://plugin.video.vimeo/play/?video_id=%s' % str(sourceId)
        else:        
            if source !='mnmedia':
                nameFormatted = '[COLOR red]'+name+'[/COLOR]'
            entry_url = sys.argv[0]+"?url="+html.normalizeUrl(the_url)+"&sourceId="+str(mediaId)

        if shortPlot == '':
            shortPlot = name.lstrip()

        liz = xbmcgui.ListItem(\
            nameFormatted, iconImage=ADDON_THUMBNAIL, thumbnailImage=iconimage)
        liz.setInfo(\
            type="Video",\
            infoLabels={\
                "Title":name,\
                "PlotOutline":shortPlot,\
                "Plot":longPlot,\
                "Duration":duree,\
                "Year":annee,\
                "Premiered":premiere}\
        )
        liz.addContextMenuItems([('Informations', 'Action(Info)')])
        setFanart(liz,fanart)
        liz.setProperty('IsPlayable', 'true')
        is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
        return is_it_ok

class ItemSC:
    def __init__(self,url,title,image):
        episode = content.getBalado(url)
      
        #if episode['subTitle'] is not None:
        #    title = title +' | [I]' + episode['subTitle']+'[/I]'
        self.item = AutoFormatDict()
        self.item['nom'] = title
        #self.item['nom']= title
        #self.item['shortPlot']= html.clean(episode['description'])
        self.item['longPlot'] =  episode
        #self.item['mediaId'] = mediaID
        self.item['sourceId'] = parse.getBaladoId(episode)
        self.item['source']=  'soundcloud'
        #self.item['isDir'] = False
        #self.item['url'] = episode['permalink']
        #self.item['credits'] = episode['credits']
        self.item['image']=image
        #self.item['fanart'] = content.getFanArt(episode['imageUrlTemplate'])
        #try:
        #    self.item['genreId'] =  episode['categories'][0]['category']['title']
        #except Exception:
        #    self.item['genreId'] = ''
        #self.item['nomComplet'] = episode['title']
        #self.item['duree'] = 0 #impossible a connaitre
        #self.item['startDate'] = episode['publishDates']['start']
        #self.item['endDate'] = episode['publishDates']['end']
        #self.item['endDateTxt'] = str(episode['publishDates']['end'])

    def __getitem__(self, key):
        return self.item[key]

    def addVideo(self):
        item = self.item
        name = item['nom']
        #the_url = item['url']
        iconimage = item['image']
        #url_info = 'none'
        #finDisponibilite = item['endDateTxt']

        
        #duree = item['duree']
        #fanart = item['fanart']
        source = item['source']
        sourceId = item['sourceId']
        #annee = item['startDate'][:4]
        #premiere = item['startDate']
        #shortPlot = item['shortPlot']
        longPlot = item['longPlot']
        #mediaId = item['mediaId']
        
        is_it_ok = True

        nameFormatted = '[BALADO] ' + name
        
        entry_url = 'plugin://plugin.audio.soundcloud/play/?audio_id=%s' % str(sourceId)
        xbmc.log('La source : '+sourceId)

        isPlayable = sourceId!=''

        try:
            sc = xbmcaddon.Addon('plugin.audio.soundcloud')
        except Exception:
            isPlayable=False
            
        if not isPlayable:
            nameFormatted = '[COLOR red]'+nameFormatted+'[/COLOR]'

        #if shortPlot == '':
        #    shortPlot = name.lstrip()

        liz = xbmcgui.ListItem(\
            nameFormatted, iconImage=iconimage)
        liz.setInfo(\
            type="Video",\
            infoLabels={\
        #        "Title":name,\
        #        "PlotOutline":shortPlot,\
                "Plot":longPlot}\
        #        "Duration":duree,\
        #        "Year":annee,\
        #        "Premiered":premiere}\
        )
        liz.addContextMenuItems([('Informations', 'Action(Info)')])
        #setFanart(liz,fanart)
        liz.setProperty('IsPlayable',str(isPlayable))
        is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)

        return is_it_ok


class ItemDummy:

    def __init__(self,title,plott='',image=ADDON_THUMBNAIL):
        self.item = AutoFormatDict()
        self.item['texte']= title
        self.item['plot'] = plott
        self.item['image'] = image
       
    def __getitem__(self, key):
        return False

    def addVideo(self):
        is_it_ok = True
        texte = self.item['texte']
        plot = self.item['plot']
        image = self.item['image']

        liz = xbmcgui.ListItem('[COLOR red]'+texte+'[/COLOR]',thumbnailImage=image)
        liz.setInfo(\
            type="Video",infoLabels={"Title":texte,"Plot":plot} )
        is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url='', listitem=liz, isFolder=False)
        return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)

