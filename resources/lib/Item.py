import content,  xbmcgui,xbmc,sys,html,xbmcplugin,parse,urllib2,urllib,xbmcaddon,simplejson

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'

__handle__ = int(sys.argv[1])

class ItemDir:

    item={}
    def __init__(self,nom,filtres,group,isDir,url,image,fanart,mode,startDate=None,resume=''):
        self.item = {'nom': urllib2.unquote(nom),'resume':resume,"filtres":filtres,\
                     'isDir':isDir,'url':url,'image':image,'fanart':fanart,'mode':mode,\
                     'startDate':startDate}
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
        
        if resume=='':
            resume = urllib.unquote(ADDON.getAddonInfo('id')+' v.'+ADDON.getAddonInfo('version'))
        if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
            resume = '[B]'+nom+'[/B][CR]'+urllib.unquote(resume)
        if iconimage=='':
            iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'



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

    item = {'nom':''}

    def __init__(self,mediaID,moreTitle = ''):
        episode = content.getShow(str(mediaID))
        title = moreTitle+episode['title']
        if episode['subTitle'] is not None:
            title = title +' | [I]' + episode['subTitle']+'[/I]'
        self.item = {'nom': title, 'resume':episode['shortDescription']}
        self.item['Plot'] = episode['description']
        self.item['mediaId'] = mediaID
        self.item['sourceId'] = episode['mediaContents'][0]['sourceId']
        self.item['source']=  episode['mediaContents'][0]['source']
        self.item['isDir'] = False
        self.item['url'] = episode['permalink']
        self.item['credits'] = episode['credits']
        self.item['image']=content.getThumbnails(episode['imageUrlTemplate'])
        self.item['fanart'] = content.getFanArt(episode['imageUrlTemplate'])
        try:
            self.item['genreId'] =  episode['categories'][0]['category']['title']
        except Exception:
            self.item['genreId'] = ''
        self.item['nomComplet'] = episode['title']
        self.item['description'] = episode['shortDescription']
        self.item['duree'] = 0 #impossible a connaitre
        self.item['startDate'] = episode['publishDates']['start']
        self.item['endDate'] = episode['publishDates']['end']
        self.item['endDateTxt'] = str(episode['publishDates']['end'])

    def __getitem__(self, key):
        return self.item[key]

    def addVideo(self):
        show = self.item
        name = html.remove_any_html_tags(show['nom'])
        the_url = show['url']
        iconimage = show['image']
        url_info = 'none'
        finDisponibilite = show['endDateTxt']

        resume = html.remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
        duree = show['duree']
        fanart = show['fanart']
        source = show['source']
        sourceId = show['sourceId']
        annee = show['startDate'][:4]
        premiere = show['startDate']
        plot = html.remove_any_html_tags(show['Plot'])
        mediaId = show['mediaId']
        
        is_it_ok = True

        nameFormatted = name
        if source !='mnmedia':
            nameFormatted = '[COLOR red]'+name+'[/COLOR]'

        entry_url = sys.argv[0]+"?url="+html.normalizeUrl(the_url)+"&sourceId="+str(mediaId)
        
        if resume != '':
            if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
                resume = '[B]'+name.lstrip()+'[/B]'+'[CR]'+resume.lstrip() 
        else:
            resume = name.lstrip()

        liz = xbmcgui.ListItem(\
            nameFormatted, iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=iconimage)
        liz.setInfo(\
            type="Video",\
            infoLabels={\
                "Title":name,\
                "PlotOutline":html.remove_any_html_tags(resume, False),\
                "Plot":html.html_unescape(html.remove_any_html_tags(plot,False)),\
                "Duration":duree,\
                "Year":annee,\
                "Premiered":premiere}\
        )
        liz.addContextMenuItems([('Informations', 'Action(Info)')])
        setFanart(liz,fanart)
        liz.setProperty('IsPlayable', 'true')
        is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
        return is_it_ok

class ItemDummy:

    texte=''
    
    def __init__(self,string):
        self.texte= string
       
    def __getitem__(self, key):
        return False

    def addVideo(self):
        is_it_ok = True
        liz = xbmcgui.ListItem(html.remove_any_html_tags(self.texte))
        liz.setInfo(\
            type="Video",infoLabels={"Title":html.remove_any_html_tags(parse.getP(self.texte)),"Plot":self.texte}       )
        is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url='', listitem=liz, isFolder=False)
        return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)

