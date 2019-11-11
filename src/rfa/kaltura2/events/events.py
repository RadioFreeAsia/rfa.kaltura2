
from KalturaClient.Plugins.Core import KalturaEntryModerationStatus

from rfa.kaltura2.kutils import kconnect
from rfa.kaltura2.kutils import KalturaLoggerInstance as logger
from rfa.kaltura2.kutils import uploadVideo
from rfa.kaltura2.kutils import rejectVideo
from rfa.kaltura2.kutils import createVideo, removeVideo
from rfa.kaltura2.kutils import kdiff
from rfa.kaltura2.kutils import setModerationStatus
from rfa.kaltura2.kutils import syncCategories

from rfa.kaltura2.adapters.kalturaMediaEntry import IKalturaMediaEntryProvider

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
    pass
    
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

    
