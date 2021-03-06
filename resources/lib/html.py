# -*- coding: utf8 -*-
# version 1.0.1 par dualB

import urllib,urllib2,xbmc,re, ssl
from log import log

def get_url_txt(the_url,data=None,verified=True):
    """ function docstring """
    log('Tentative de connection a : ' + the_url)
    if data is None:
        req = urllib2.Request(the_url)
    else:
        req = urllib2.Request(the_url,urllib.urlencode(data))
    req.add_header(\
                       'User-Agent', \
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'\
                       )
    req.add_header('Accept-Charset', 'utf-8')
    try:
        context = None
        if not verified:
            log('Requete en SSL NON VERIFIE')
            context = ssl._create_unverified_context()
        response = urllib2.urlopen(req,context=context)	
        link = response.read()
        link = urllib2.quote(link)
        link = urllib2.unquote(link)
        response.close()
        return link
    except urllib2.HTTPError, e:
        log('HTTPError = ' + str(e.code))
        return ''
    except urllib2.URLError, e:
        log('URLError = ' + str(e.reason))
        return ''
    except httplib.HTTPException, e:
        log('HTTPException')
        return ''
    except:
        log('ERREUR NON PREVUE')
        return ''


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
        'yacute':'ý', 'yuml':'ÿ', 'rsquo':'\''
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

def clean(data):
    return remove_any_html_tags( html_unescape(data),False)

def html_unescape(data):
    """ function docstring """
    data = re.sub(r'&#?x?(\w+);|\\\\u\d{4}', unescape_callback, data)
    return data

def normalizeUrl(the_url):
    try:
        the_url =  unicodedata.normalize("NFKD", the_url)
        return urllib.quote_plus(the_url)
    except Exception:
        return the_url


RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

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
