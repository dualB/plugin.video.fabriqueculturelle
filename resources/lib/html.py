# -*- coding: utf8 -*-

# version 1.0.0 - By CB

import urllib,urllib2,xbmc,re

def get_url_txt(the_url):
    """ function docstring """
    req = urllib2.Request(the_url)
    req.add_header(\
        'User-Agent',\
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'\
    )
    req.add_header('Accept-Charset', 'utf-8')
    response = urllib2.urlopen(req)
    link = response.read()
    #link = urllib2.quote(link)
    #link = urllib2.unquote(link)
    response.close()
    return link

def get_url_txt_post(the_url,data):
    """ function docstring """
    req = urllib2.Request(the_url,urllib.urlencode(data))
    req.add_header(\
        'User-Agent',\
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'\
    )
    req.add_header('Accept-Charset', 'utf-8')
    response = urllib2.urlopen(req)
    link = response.read()
 ##   link = html_unescape(link)
    link = urllib2.quote(link)
    link = urllib2.unquote(link)
    
    response.close()
    return link   

# Merci à l'auteur de cette fonction
def unescape_callback(matches):
    """ function docstring """
    html_entities = \
    {
        'quot':'\"', 'amp':'&', 'apos':'\'', 'lt':'<',
        'gt':'>', 'nbsp':' ', 'copy':'©', 'reg':'®',
        'Agrave':'À', 'Aacute':'Á', 'Acirc':'Â',
        'Atilde':'Ã', 'Auml':'Ä', 'Aring':'Å',
        'AElig':'Æ', 'Ccedil':'Ç', 'Egrave':'È',
        'Eacute':'É', 'Ecirc':'Ê', 'Euml':'Ë',
        'Igrave':'Ì', 'Iacute':'Í', 'Icirc':'Î',
        'Iuml':'Ï', 'ETH':'Ð', 'Ntilde':'Ñ',
        'Ograve':'Ò', 'Oacute':'Ó', 'Ocirc':'Ô',
        'Otilde':'Õ', 'Ouml':'Ö', 'Oslash':'Ø',
        'Ugrave':'Ù', 'Uacute':'Ú', 'Ucirc':'Û',
        'Uuml':'Ü', 'Yacute':'Ý', 'agrave':'à',
        'aacute':'á', 'acirc':'â', 'atilde':'ã',
        'auml':'ä', 'aring':'å', 'aelig':'æ',
        'ccedil':'ç', 'egrave':'è', 'eacute':'é',
        'ecirc':'ê', 'euml':'ë', 'igrave':'ì',
        'iacute':'í', 'icirc':'î', 'iuml':'ï',
        'eth':'ð', 'ntilde':'ñ', 'ograve':'ò',
        'oacute':'ó', 'ocirc':'ô', 'otilde':'õ',
        'ouml':'ö', 'oslash':'ø', 'ugrave':'ù',
        'uacute':'ú', 'ucirc':'û', 'uuml':'ü',
        'yacute':'ý', 'yuml':'ÿ'
    }

    entity = matches.group(0)
    val = matches.group(1)

    try:
        if entity[:2] == r'\u':
            return entity.decode('unicode-escape')
        elif entity[:3] == '&#x':
            return unichr(int(val, 16))
        elif entity[:2] == '&#':
            return unichr(int(val))
        else:
            return html_entities[val].decode('utf-8')

    except (ValueError, KeyError):
        pass

def html_unescape(data):
    """ function docstring """
    data = data.decode('utf-8')
    data = re.sub(r'&#?x?(\w+);|\\\\u\d{4}', unescape_callback, data)
    data = data.encode('utf-8')
    return data
