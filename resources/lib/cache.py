# -*- coding: cp1252 -*-
# version 1.0.1 par dualB
""" -*- coding: utf-8 -*- """


import xbmcaddon, os, xbmc, time, sys, html
from log import log

ADDON = xbmcaddon.Addon()
ADDON_CACHE_BASEDIR = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('path')), ".cache")
ADDON_CACHE_TTL = float(ADDON.getSetting('CacheTTL').replace("0", ".5").replace("73", "0"))

if not os.path.exists(ADDON_CACHE_BASEDIR):
    os.makedirs(ADDON_CACHE_BASEDIR)

if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash

def is_cached_content_expired(last_update):
    """ function docstring """
    expired = time.time() >= (last_update + (ADDON_CACHE_TTL * 60**2))
    return expired

def get_cached_content(path,verified=True):
    """ function docstring """
    content = None
    try:
        filename = get_cached_filename(path)
        if os.path.exists(filename) and not is_cached_content_expired(os.path.getmtime(filename)):
            content = open(filename).read()
        else:
            content = html.get_url_txt(path,None,verified)
            try:
                file(filename, "w").write(content) # cache the requested web content
            except StandardError:
                log('Impossible de sauvegarder le contenu : ' +path)
                traceback.print_exc()
    except StandardError:
        log('Impossible de trouver le contenu : ' +path)
        return None
    return content

def get_cached_path(path):
    """ function docstring """
    content = None
    try:
        filename = get_cached_filename(path)
        if os.path.exists(filename) and not is_cached_content_expired(os.path.getmtime(filename)):
            content = open(filename).read()
        else:
            content = html.get_url_txt(path)
            if len(content)>0:
                try:
                    file(filename, "w").write(content) # cache the requested web content
                except StandardError:
                    log('Impossible decrire le fichier cache')
                    traceback.print_exc()
    except StandardError:
        return None
    return filename


def get_cached_filename(path):
    """ function docstring """
    filename = "%s" % _hash(repr(path)).hexdigest()
    return os.path.join(ADDON_CACHE_BASEDIR, filename)
