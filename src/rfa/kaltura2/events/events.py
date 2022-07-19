import logging


from KalturaClient.Plugins.Core import KalturaEntryModerationStatus
from KalturaClient.Plugins.Core import KalturaUploadedFileTokenResource
from KalturaClient.Plugins.Core import KalturaThumbParams, KalturaThumbCropType, KalturaContainerFormat, KalturaBaseUser
from KalturaClient.exceptions import KalturaException

from rfa.kaltura2.kutils import kconnect
from rfa.kaltura2.kutils import KalturaLoggerInstance as logger
from rfa.kaltura2.kutils import uploadVideo
from rfa.kaltura2.kutils import rejectVideo
from rfa.kaltura2.kutils import uploadThumbnail
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

    #upload custom thumbnail
    if context.custom_thumbnail:
        addThumbnail(context, event)
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
    thumbnail_changed = False

    if hasattr(event, 'descriptions') and event.descriptions:
        for d in event.descriptions:
            if d.interface is IKaltura_Video and 'video_file' in d.attributes:
                file_changed = True
            if d.interface is IKaltura_Video and 'custom_thumbnail' in d.attributes:
                thumbnail_changed = True
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

    if thumbnail_changed:
        modify_thumbnail(context, event, entryId)

    syncCategories(context, client)

def modify_thumbnail(context, event, enteryId):

    (client, session) = kconnect()
    thumb_assets = client.thumbAsset.getByEntryId(enteryId)
    default_thumb_id = None
    #get default_thumb and delete it after making new upload default
    for i in thumb_assets:
        if i.getTags() == 'default_thumb':
            default_thumb_id = i.getId()

    if context.custom_thumbnail:

        new_thumbnail = uploadThumbnail(context, client)
        asset_id = new_thumbnail.id
        #make new upload default and delete previous default
        client.thumbAsset.setAsDefault(asset_id)
        if default_thumb_id:
            client.thumbAsset.delete(default_thumb_id)
    #if request is to remove, then generate a thumb from video and make it default and remove previous default
    else:
        thumb_params = KalturaThumbParams()
        thumb_params.cropType = KalturaThumbCropType.CROP
        thumb_params.format = KalturaContainerFormat.JPG
        thumb_params.videoOffset = 15
        source_asset_id = ""
        result = client.thumbAsset.generate(enteryId, thumb_params, source_asset_id)
        client.thumbAsset.setAsDefault(result.getId())

        thumb_assets = client.thumbAsset.getByEntryId(enteryId)
        for i in thumb_assets:
            if i.getTags() != 'default_thumb':
                client.thumbAsset.delete(i.getId())

def deleteVideo(context, event):
    ##TODO - configure option to delete or reject plone deleted content.
    #kremoveVideo(context)

    #Now, we only reject videos deleted in plone, to support an undo action.
    rejectVideo(context)

def addThumbnail(context, event):

    (client, session) = kconnect()

    thumbnail = uploadThumbnail(context, client)
    asset_id = thumbnail.id
    client.thumbAsset.setAsDefault(asset_id)

def workflowChange(context, event):
    workflow = event.workflow
    action = event.action
    status = None

    if action == 'publish':
        status = KalturaEntryModerationStatus.APPROVED
        effective_date = context.effective_date
        if effective_date:
            python_date = effective_date.asdatetime()
            epoch_date = python_date.timestamp()
            mediaEntry = getattr(context, 'KalturaObject', None)
            if mediaEntry is not None:
                mediaEntry.setStartDate(epoch_date)
                newMediaEntry = IKalturaMediaEntryProvider(context).getEntry()
                (client, session) = kconnect()
                mediaEntry = client.media.update(mediaEntry.id, newMediaEntry)
    elif action in ('retract', 'reject'):
        status = KalturaEntryModerationStatus.PENDING_MODERATION

    if status:
        setModerationStatus(context, status)


