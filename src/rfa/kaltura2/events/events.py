import logging


from KalturaClient.Plugins.Core import KalturaEntryModerationStatus
from KalturaClient.Plugins.Core import KalturaUploadedFileTokenResource
from KalturaClient.exceptions import KalturaException

from rfa.kaltura2.kutils import kconnect
from rfa.kaltura2.kutils import KalturaLoggerInstance as logger
from rfa.kaltura2.kutils import uploadVideo
from rfa.kaltura2.kutils import rejectVideo
from rfa.kaltura2.kutils import createVideo, removeVideo
from rfa.kaltura2.kutils import kdiff
from rfa.kaltura2.kutils import setModerationStatus
from rfa.kaltura2.kutils import syncCategories

from rfa.kaltura2.adapters.kalturaMediaEntry import IKalturaMediaEntryProvider
from rfa.kaltura2.kaltura_video import IKaltura_Video

def addVideo(context, event):
    """When a video is added to a container
       zope.lifecycleevent.interfaces.IObjectAddedEvent"""
    
    #adapt the Plone video to a Kaltura Video Media Entry
    mediaEntry = IKalturaMediaEntryProvider(context).getEntry()
    (client, session) = kconnect()
    
    #Do the upload of the video file
    uploadTokenId = uploadVideo(context, client)
    
    #associate the upload with this mediaEntry
    mediaEntry = client.media.addFromUploadedFile(mediaEntry, uploadTokenId)
    
    #associate the KalturaMediaObject with the Plone Video
    context.KalturaObject = mediaEntry
    
    #make sure categories set in Plone are set for this MediaEntry
    syncCategories(context, client)
    
        
def modifyVideo(context, event):
    """Fired when the object is edited
       Any differences between plone object (context) and kaltura object
       are considered edits to the kaltura object, and are sent to kaltura
    """
    newMediaEntry = IKalturaMediaEntryProvider(context).getEntry()
    entryId = context.KalturaObject.getId()
    file_changed = False
    if hasattr(event, 'descriptions') and event.descriptions:
        for d in event.descriptions:
            if d.interface is IKaltura_Video and 'video_file' in d.attributes:
                file_changed = True
                
    (client, session) = kconnect()
    
    mediaEntry = client.media.update(entryId, newMediaEntry)
    context.KalturaObject = mediaEntry
    
    if file_changed:
        logger.log('uploading new video for %s' % (context.getId(),),
               level=logging.WARN)
    
        uploadTokenId = uploadVideo(context, client)
        resource = KalturaUploadedFileTokenResource()
        resource.setToken(uploadTokenId)
        try:
            client.media.updateContent(entryId, resource)
        except KalturaException as e:
            if e.code == 'ENTRY_REPLACEMENT_ALREADY_EXISTS':
                #auto-deny the half-cooked replacement and re-try
                client.media.cancelReplace(entryId)
                client.media.updateContent(entryId, resource)

        #XXX if 'auto approve' is turned off in settings:
        try:
            newMediaEntry = client.media.approveReplace(entryId)
        except KalturaException as e:
            if e.code == 'ENTRY_ID_NOT_REPLACED':
                logger.log('Kaltura Video not replaced on KMC for %s, entry id %s' %(context.getId(), entryId),
                           level=logging.WARN)
                   
    syncCategories(context, client)     
    
def deleteVideo(context, event):
    ##TODO - configure option to delete or reject plone deleted content.
    #kremoveVideo(context)  
    
    #Now, we only reject videos deleted in plone, to support an undo action.
    rejectVideo(context)
    
def workflowChange(context, event):
    workflow = event.workflow
    action = event.action
    status = None
    
    if action == 'publish':
        status = KalturaEntryModerationStatus.APPROVED
    elif action in ('retract', 'reject'):
        status = KalturaEntryModerationStatus.PENDING_MODERATION
    
    if status:
        setModerationStatus(context, status)

    
