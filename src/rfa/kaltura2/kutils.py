
import logging
import sys

from rfa.kaltura2 import credentials

from KalturaClient import *
from KalturaClient.Base import IKalturaLogger
from KalturaClient.Base import KalturaConfiguration
from KalturaClient.exceptions import KalturaException
from KalturaClient.Plugins.Core import KalturaSessionType
from KalturaClient.Plugins.Core import KalturaPlaylist, KalturaPlaylistType
from KalturaClient.Plugins.Core import KalturaMediaEntry, KalturaMediaType
from KalturaClient.Plugins.Core import KalturaUiConf, KalturaUiConfObjType, KalturaUiConfFilter
from KalturaClient.Plugins.Core import KalturaMediaEntryFilter, KalturaMediaEntryFilterForPlaylist
from KalturaClient.Plugins.Core import KalturaMediaEntryOrderBy
from KalturaClient.Plugins.Core import KalturaCategoryFilter
from KalturaClient.Plugins.Core import KalturaCategoryEntry
from KalturaClient.Plugins.Core import KalturaSearchOperator
from KalturaClient.Plugins.Core import KalturaUploadToken, KalturaUploadedFileTokenResource
from KalturaClient.Plugins.Core import KalturaEntryModerationStatus

logger = logging.getLogger("rfa.kaltura")
logger.setLevel(logging.WARN)

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    stream = sys.stdout)

class KalturaLogger(IKalturaLogger):
    def log(self, msg, summary='', level=logging.DEBUG):
        logger.log(level, '%s \n%s', summary, msg)
        
KalturaLoggerInstance = KalturaLogger()


#monkeypatch for testing purposes
getCredentials = credentials.getCredentials


def kconnect(partner_id=None):
    
    creds = getCredentials()
    if partner_id is not None:
        creds['PARTNER_ID'] = partner_id
    
    privacyString = ''    

    #may want to add 'disableentitlements' to the privacyString eventuall for users who want to
    # disable all entitlement checking
    if creds.get('PRIVACY_CONTEXT', '') not in ('', None):
        privacyString = 'privacycontext:' + creds['PRIVACY_CONTEXT']
        
    
    config = KalturaConfiguration(creds['PARTNER_ID'])
    config.serviceUrl = creds['SERVICE_URL']
    config.setLogger(KalturaLoggerInstance)
        
    client = KalturaClient(config)
    
    # start new session
    ks = client.generateSession(creds['ADMIN_SECRET'], 
                                creds['USER_NAME'],
                                KalturaSessionType.ADMIN, 
                                creds['PARTNER_ID'],
                                86400,
                                privacyString)
    client.setKs(ks)    
    
    return (client, ks)


def kGetPlaylistPlayers():
    return tuple()

def kGetVideoPlayers():
    (client, session) = kconnect()

    filt = KalturaUiConfFilter()
    players = [KalturaUiConfObjType.PLAYER_V3,
               KalturaUiConfObjType.PLAYER,
               KalturaUiConfObjType.PLAYER_SL,
               ]
    tags = 'player'

    filt.setObjTypeIn(players)
    filt.setTagsMultiLikeOr(tags)
    resp = client.uiConf.list(filter=filt)
    objs = resp.objects

    return objs    

class dummy_category_object(object):
    id = 1
    name = 'foo'
    def getId(self):
        return self.id
    def getName(self):
        return self.name

def kGetCategories(parent=None):
    obj = dummy_category_object()
    obj2 = dummy_category_object()
    obj2.id = 2
    obj2.name = 'bar'
    return [obj, obj2]

def kGetCategoryId(categoryName):
    return "fake id"

