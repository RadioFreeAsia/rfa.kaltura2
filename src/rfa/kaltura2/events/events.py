
from rfa.kaltura2.kutils import kconnect
from rfa.kaltura2.kutils import KalturaLoggerInstance as logger
from rfa.kaltura2.kutils import kupload, kcreatePlaylist, kcreateVideo, kremoveVideo, krejectVideo
from rfa.kaltura2.kutils import kdiff
from rfa.kaltura2.kutils import kSetStatus, KalturaEntryModerationStatus


def addVideo(context, event):
    """When a video is added to a container
       zope.lifecycleevent.interfaces.IObjectAddedEvent"""
    import pdb; pdb.set_trace()
    pass
        
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
    krejectVideo(context)
    
def workflowChange(context, event):
    workflow = event.workflow
    action = event.action
    status = None
    
    if action == 'publish':
        status = KalturaEntryModerationStatus.APPROVED
    elif action in ('retract', 'reject'):
        status = KalturaEntryModerationStatus.PENDING_MODERATION
    
    if status:
        context.setModerationStatus(status)

    
