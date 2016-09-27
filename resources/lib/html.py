# -*- coding: cp1252 -*-

""" -*- coding: utf-8 -*- """
# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB

import urllib2,re, socket


# Merci � l'auteur de cette fonction
def unescape_callback(matches):
    """ function docstring """
    html_entities =\
    {
        'quot':'\"', 'amp':'&', 'apos':'\'', 'lt':'<',
        'gt':'>', 'nbsp':' ', 'copy':'�', 'reg':'�',
        'Agrave':'�', 'Aacute':'�', 'Acirc':'�',
        'Atilde':'�', 'Auml':'�', 'Aring':'�',
        'AElig':'�', 'Ccedil':'�', 'Egrave':'�',
        'Eacute':'�', 'Ecirc':'�', 'Euml':'�',
        'Igrave':'�', 'Iacute':'�', 'Icirc':'�',
        'Iuml':'�', 'ETH':'�', 'Ntilde':'�',
        'Ograve':'�', 'Oacute':'�', 'Ocirc':'�',
        'Otilde':'�', 'Ouml':'�', 'Oslash':'�',
        'Ugrave':'�', 'Uacute':'�', 'Ucirc':'�',
        'Uuml':'�', 'Yacute':'�', 'agrave':'�',
        'aacute':'�', 'acirc':'�', 'atilde':'�',
        'auml':'�', 'aring':'�', 'aelig':'�',
        'ccedil':'�', 'egrave':'�', 'eacute':'�',
        'ecirc':'�', 'euml':'�', 'igrave':'�',
        'iacute':'�', 'icirc':'�', 'iuml':'�',
        'eth':'�', 'ntilde':'�', 'ograve':'�',
        'oacute':'�', 'ocirc':'�', 'otilde':'�',
        'ouml':'�', 'oslash':'�', 'ugrave':'�',
        'uacute':'�', 'ucirc':'�', 'uuml':'�',
        'yacute':'�', 'yuml':'�'
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
    #link = html_unescape(link)
    link = urllib2.quote(link)
    link = urllib2.unquote(link)
    response.close()
    return link


def is_network_available(url):
    """ function docstring """
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(url)
        # connect to the host -- tells us if the host is actually reachable
        srvcon = socket.create_connection((host, 80), 2)
        srvcon.close()
        return True
    except socket.error:
        return False



