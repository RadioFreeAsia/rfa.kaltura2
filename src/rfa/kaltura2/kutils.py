import tempfile
import logging
import sys
import os
from copy import copy

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

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
from KalturaClient.Plugins.Core import KalturaCategoryEntryFilter
from KalturaClient.Plugins.Core import KalturaCategoryFilter
from KalturaClient.Plugins.Core import KalturaCategoryEntry
from KalturaClient.Plugins.Core import KalturaSearchOperator
from KalturaClient.Plugins.Core import KalturaUploadToken, KalturaUploadedFileTokenResource
from KalturaClient.Plugins.Core import KalturaEntryModerationStatus

from rfa.kaltura2 import credentials
from rfa.kaltura2.controlpanel import IRfaKalturaSettings

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


#@cache me?
def GetVideoPlayers():
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


#@cache me?
def GetPlaylistPlayers():
    (client, session) = kconnect()
    
    filt = KalturaUiConfFilter()
    players = [KalturaUiConfObjType.PLAYER_V3,]
    tags = 'playlist'
        
    filt.setObjTypeIn(players)
    filt.setTagsMultiLikeOr(tags)
       
    resp = client.uiConf.list(filter=filt)
    objs = resp.objects
    
    return objs

def getVideo(videoId):
    (client, session) = kconnect()
    result = client.media.get(videoId)
    return result

def makeFilter(catIds=None, tagIds=None, order=None):
    """Helper function for creating KalturaMediaEntryFilters
    """
    kfilter = KalturaMediaEntryFilter()

    if order is not None:
        kfilter.setOrderBy(order)
    
    if catIds is not None:
        if isinstance(catIds, list) or isinstance(catIds, tuple):
            catIds = ','.join(catIds)   
        kfilter.setCategoryAncestorIdIn(catIds)
        
    return kfilter
    #if tagIds is not None....

def getRecent(limit=10, partner_id=None, filt=None):
    """Get the most recently uploaded videos
       provide 'filt' parameter of an existing KalturaMediaEntryFilter to filter results
    """
    if filt is not None:
        kfilter = copy(filt)
    else:
        kfilter = KalturaMediaEntryFilter()
    kfilter.setOrderBy(KalturaMediaEntryOrderBy.CREATED_AT_DESC)
    (client, session) = kconnect(partner_id)
    result = client.media.list(filter=kfilter)
    return result.objects

def getMostViewed(limit=10, partner_id=None, filt=None):
    """Get videos ranked by views
       provide 'filt' parameter of an existing KalturaMediaEntryFilter to filter results
    """
    if filt is not None:
        kfilter = copy(filt)
    else:
        kfilter = KalturaMediaEntryFilter()
    kfilter.setOrderBy(KalturaMediaEntryOrderBy.VIEWS_DESC)
    (client, session) = kconnect(partner_id)
    result = client.media.list(filter=kfilter)
    return result.objects

def getTagVids(tags, limit=10, partner_id=None, filt=None):
    """Get all videos that contain one or more querytags
       provide a non-string iterable as tags parameter
       provide 'filt' parameter of an existing KalturaMediaEntryFilter to filter results
    """
    if isinstance(tags, str):
        raise TypeError("tags must be a non-string iterable")
    
    if filt is not None:
        kfilter = copy(filt)
    else:
        kfilter = KalturaMediaEntryFilter()    

    kfilter.setOrderBy(KalturaMediaEntryOrderBy.CREATED_AT_DESC)
    
    try:
        querytags = ','.join(tags)
    except TypeError:
        raise TypeError("tags must be a non-string iterable")
    
    kfilter.setTagsMultiLikeOr(querytags)
    
    (client, session) = kconnect(partner_id)
    result = client.media.list(filter=kfilter)
    return result.objects    

def getCategoryVids(catId, limit=10, partner_id=None, filt=None):
    """ Get videos placed in the provided category id, or child categories
        provide 'filt' parameter of an existing KalturaMediaEntryFilter to filter results
    """
    if filt is not None:
        kfilter = copy(filt)
    else:
        kfilter = KalturaMediaEntryFilter()
    kfilter.setOrderBy(KalturaMediaEntryOrderBy.CREATED_AT_DESC)
    kfilter.setCategoryAncestorIdIn(catId)
    (client, session) = kconnect(partner_id)
    result = client.media.list(filter=kfilter)
    return result.objects

def getRelated(kvideoObj, limit=10, partner_id=None, filt=None):
    """ Get videos related to the provided video
        provide 'filt' parameter of an existing KalturaMediaEntryFilter to filter results
    """
    tags = kvideoObj.getTags().split()
    return getTagVids(tags, limit, partner_id, filt)

def createEmptyFilterForPlaylist():
    """Create a Playlist Filter, filled in with default, required values"""
    #These were mined by reverse-engineering a playlist created on the KMC and inspecting the object
    kfilter = KalturaMediaEntryFilterForPlaylist()
    
    kfilter.setLimit(30)
    kfilter.setModerationStatusIn('2,5,6,1')
    kfilter.setOrderBy('-plays')
    kfilter.setStatusIn('2,1')
    kfilter.setTypeIn('1,2,7')
    
    return kfilter   

def createPlaylist(context):
    """Create an empty playlist on the kaltura server"""
    
    kplaylist = KalturaPlaylist()
    kplaylist.setName(context.Title())
    kplaylist.setDescription(context.Description())
    kplaylist.setReferenceId(context.UID())
    
    if IKalturaManualPlaylist.providedBy(context):
        kplaylist.setPlaylistType(KalturaPlaylistType(KalturaPlaylistType.STATIC_LIST))
    elif IKalturaRuleBasedPlaylist.providedBy(context):
        kplaylist.setPlaylistType(KalturaPlaylistType(KalturaPlaylistType.DYNAMIC))
        maxVideos = getattr(context, 'maxVideos', DEFAULT_DYNAMIC_PLAYLIST_SIZE)
        kplaylist.setTotalResults(maxVideos)
        kfilter = kcreateEmptyFilterForPlaylist()
        kfilter.setFreeText(','.join(context.getTags()))

        kfilter.setCategoriesIdsMatchOr(','.join(context.getCategories()))
        kplaylist.setFilters([kfilter])
    else:
        raise AssertionError("%s is not a known playlist type" % (context.portal_type,))
    
    (client, session) = kconnect()
    
    kplaylist = client.playlist.add(kplaylist)
    
    return kplaylist

def createVideo(context):
    """given a plone content-type of kalturavideo,
       create a Kaltura MediaEntry object.
       The mediaEntry ReferenceId is set to the UID of the plone object 
       to tie them together
    """
    mediaEntry = KalturaMediaEntry()
    mediaEntry.setName(context.Title())
    mediaEntry.setMediaType(KalturaMediaType(KalturaMediaType.VIDEO))
    mediaEntry.searchProviderId = context.UID() #XXX Is this correct?  We assign this to the file UID stored in plone.
    
    #kaltura referenceId == plone UID
    mediaEntry.setReferenceId(context.UID())
    if len(context.getCategories()):
        mediaEntry.setCategoriesIds(','.join([c for c in context.getCategories() if c]))    
    if len(context.getTags()):
        mediaEntry.setTags(','.join([t for t in context.getTags() if t]))
    
    return mediaEntry
    
def uploadVideo(context, client=None):
    """Provide the KalturaVideo with a NamedFile field.
       This uploads the video to Kaltura and returns the upload token.
        """
    usingEntitlements = False
    
    #get the file field and....
    
    field = context.video_file
    if field.filename is None:
        return 1 #there is no file.
    
    #XXX Configure Temporary Directory and name better
    
    #XXX Try to make this a thread and signal back to context when upload complete
    #XXX Turn into a file stream from context.get_data to avoid write to file...
    
    #When we try to use temporary file, kaltura throws an exception
    #Module KalturaClient.Plugins.Core, line 64352, in upload
    #    Module KalturaClient.Client, line 364, in doQueue
    #    Module KalturaClient.Client, line 316, in doHttpRequest
    #    Module KalturaClient.Client, line 298, in openRequestUrl
    # *** KalturaClient.exceptions.KalturaClientException: expected string or bytes-like object (-4)
    # I think it's the filename property of the tempfile being an integer - but not enough analysis to be sure.
    #tempfh = tempfile.TemporaryFile(mode="w+b")
    #tempfh.write(field.data)
    #tempfh.seek(0)
    
    #So, we go through this inefficient little jig until we figure out a better way
    tempfh = open('/tmp/tempfile', 'wb')
    tempfh.write(field.data)
    tempfh.close()  #reopen?
    tempfh = open('/tmp/tempfile', 'rb')    
    
    name = context.title
    ProviderId = context.UID()  
     
    if client is None:
        (client, session) = kconnect()
    
    uploadToken = client.uploadToken.add()
    client.uploadToken.upload(uploadToken.id, tempfh)
    
    #unnecessary if we use TemporaryFile
    tempfh.close()
    os.remove('/tmp/tempfile')
  
    KalturaLoggerInstance.log("video uploaded to kaltura: uploadToken.id %s" % (uploadToken.id,))
    
    #remove local blob if configured to do so.
    #if "no local storage" is set, we clobber the blob file.
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IRfaKalturaSettings)
    if settings.storageMethod == u"No Local Storage":    
        field.data = name+"\n\nThis file is stored on kaltura only, and is not available via plone"

    return uploadToken.id
    
def removeVideo(context):
    (client, session) = kconnect()
    try:
        client.media.delete(context.KalturaObject.getId())
    except: #XXX ENTRY_ID_NOT_FOUND exception, specifically
        pass
    
def rejectVideo(context):
    (client, session) = kconnect()
    try:
        client.media.reject(context.KalturaObject.getId())
    except: #XXX ENTRY_ID_NOT_FOUND exception, specifically
        pass
    
#XXX cacheme for a few mins
def GetCategories(parent=None):
    (client, session) = kconnect()
    
    if parent is not None:
        filt = KalturaCategoryFilter()
        filt.setAncestorIdIn(parent)
    else:
        filt = None
    
    result = client.category.list(filter=filt).objects
    return result

def GetCategoryId(categoryName):
    """ provide a categoryName (string) and this will return it's Id on the kaltura server"""
    categoryObjs = GetCategories()
    for cat in categoryObjs:
        if cat.getName() == categoryName:
            return cat.getId()
        
    return None

def GetCategoryName(categoryId):
    """ provide a categoryId and this will return it's name on the kaltura server"""
    categoryObjs = GetCategories()
    categoryId = int(categoryId)
    for cat in categoryObjs:
        if cat.getId() == categoryId:
            return cat.getName()
        
    return None

def kdiff(ploneObj, kalturaObj):
    """do a property-to-property match between plone object and kaltura object
       and return property name tuples of fields that differ
       Useful to keep plone and kaltura in sync when edits occur.
    """
    
    def getvals(pFieldName, kFieldName):
        pval = getattr(ploneObj, pFieldName)
        if callable(pval):
            pval = pval()
        kval = getattr(kalturaObj, kFieldName)
        if callable(kval):
            kval = kval()
            
        return (pval, kval)
        
    retval = []
    #supported scalar properties that sync (kalturaVideo(plone), KalturaMediaEntry(kmc))
    scalarFields = [ ('Title', 'getName'),
                     ('Description', 'getDescription'),
                     ('getPartnerId', 'getPartnerId')
                   ]

    for (ploneField, kalturaField) in scalarFields:
        pval, kval = getvals(ploneField, kalturaField)
        if kval != pval:
            retval.append( (ploneField, kalturaField) )
            
    #compare moderation status / workflow ###TODO

    #compare categories:
    pval = set(ploneObj.getCategories())
    kval = set(kalturaObj.getCategoriesIds().split(','))
    
    if pval != kval:
        retval.append( ('getCategories', 'getCategoriesIds'))

    #compare tags:
    pval = set(ploneObj.getTags())
    kval = set(kalturaObj.getTags().split(','))
    
    if pval != kval:
        retval.append(('getTags', 'getTags'))

    return retval


def setModerationStatus(context, status, client=None):
    """given a kaltura video object, set the status on the media entry
       and update the server
       PENDING_MODERATION = 1
       APPROVED = 2
       REJECTED = 3
       FLAGGED_FOR_REVIEW = 5
       AUTO_APPROVED = 6
    """
    
    if client is None:
        client, ks = kconnect()
    
    if status in (2,):
        updateEntry = client.media.approve(context.KalturaObject.getId())
    elif status in (3,1,5):
        updateEntry = client.media.reject(context.entryId)
        
    #TODO: create moderationFlag object and flag entry.
    
    return updateEntry
    
    
def syncCategories(context, client=None, categories=None):
    
    if categories is None:
        categories = context.categories
    newCatEntries = []
    
    if client is None:
        (client, session) = kconnect()
        
    #refresh list of categories from server, and sync to plone object
    filt = KalturaCategoryEntryFilter()
    filt.setEntryIdEqual(context.KalturaObject.getId())
    categoryEntries = client.categoryEntry.list(filt).objects

    #current set is the set of categories on Kaltura service (remote)
    currentSet = set([catEntry.categoryId for catEntry in categoryEntries])
    
    #New set is the set of categories on our context
    newSet = set([int(catId) for catId in categories])
        
    #determine what categories need to be added
    addCats = newSet.difference(currentSet)
    
    #determine what categories need to be removed
    delCats = currentSet.difference(newSet)
   
    #do adds
    for catId in addCats:
        newCatEntry = KalturaCategoryEntry()
        newCatEntry.setCategoryId(catId)
        newCatEntry.setEntryId(context.KalturaObject.getId())
        try:
            client.categoryEntry.add(newCatEntry)
        except KalturaException as e:
            if e.code == "CATEGORY_ENTRY_ALREADY_EXISTS":
                pass #should never happen, tho
    
    #do removes
    for catId in delCats:
        client.categoryEntry.delete(context.KalturaObject.getId(), catId)
        
    #sync the categories to plone object
    kCategoryEntries = client.categoryEntry.list(filt).objects
    remoteCategories = [str(obj.categoryId) for obj in kCategoryEntries]
    context.categories = remoteCategories
    
    