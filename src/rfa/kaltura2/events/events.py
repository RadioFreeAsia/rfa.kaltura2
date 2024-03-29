import logging

from zope.container.interfaces import INameChooser
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.locking.interfaces import ILockable

from KalturaClient.Plugins.Core import KalturaEntryModerationStatus
from KalturaClient.Plugins.Core import KalturaUploadedFileTokenResource
from KalturaClient.exceptions import KalturaException

from rfa.kaltura2.kutils import kconnect
from rfa.kaltura2.kutils import KalturaLoggerInstance as logger
from rfa.kaltura2.kutils import rejectVideo
from rfa.kaltura2.kutils import uploadThumbnail
from rfa.kaltura2.kutils import setModerationStatus
from rfa.kaltura2.kutils import syncCategories

from rfa.kaltura2.adapters.kalturaMediaEntry import IKalturaMediaEntryProvider
from rfa.kaltura2.kaltura_video import IKaltura_Video

import transaction

def addVideo(context, event):
    """When a video is added to a container
       zope.lifecycleevent.interfaces.IObjectAddedEvent"""

    #adapt the Plone video to a Kaltura Video Media Entry
    mediaEntry = IKalturaMediaEntryProvider(context).getEntry()
    (client, session) = kconnect()

    #associate the upload with this mediaEntry
    mediaEntry = client.media.addFromUploadedFile(mediaEntry, context.upload_token_id)

    #associate the KalturaMediaObject with the Plone Video
    context.KalturaObject = mediaEntry

    #upload custom thumbnail
    if context.custom_thumbnail:
        addThumbnail(context, event)
    #make sure categories set in Plone are set for this MediaEntry
    syncCategories(context, client)

    #Try to set the id of the kaltura video based on the filename of the uploaded file.
    new_name = context.REQUEST.form.get('video_file_name')

    if new_name:
        # Gleefully stolen from plone.app.dexterity.behaviors.id
        context = aq_inner(context)
        parent = aq_parent(context)
        if parent is None:
            # Object hasn't been added to graph yet; just set directly
            context.id = new_name
            return
        new_id = INameChooser(parent).chooseName(new_name, context)
        if getattr(aq_base(context), 'id', None):
            transaction.savepoint()
            locked = False
            lockable = ILockable(context, None)
            if lockable is not None and lockable.locked():
                locked = True
                lockable.unlock()
            parent.manage_renameObject(context.getId(), new_id)
            if locked:
                lockable.lock()
        else:
            context.id = new_id

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
        for descr in event.descriptions:
            if descr.interface is IKaltura_Video and 'upload_token_id' in descr.attributes:
                file_changed = True
            if descr.interface is IKaltura_Video and 'custom_thumbnail' in descr.attributes:
                thumbnail_changed = True

    (client, session) = kconnect()
    mediaEntry = client.media.update(entryId, newMediaEntry)
    context.KalturaObject = mediaEntry

    if file_changed:
        uploadTokenId = context.upload_token_id
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
    thumb_id = None
    default_thumb_id = None
    #get default_thumb and other thumb
    for i in thumb_assets:
        if i.getTags() == 'default_thumb':
            default_thumb_id = i.getId()

        if i.getTags() != 'default_thumb':
            thumb_id = i.getId()

    if context.custom_thumbnail:

        new_thumbnail = uploadThumbnail(context, client)
        asset_id = new_thumbnail.id
        #make new upload default
        client.thumbAsset.setAsDefault(asset_id)

    #if request is to remove,
    else:
        for i in thumb_assets:
            if i.getTags() == 'default_thumb':
                if thumb_id:
                    client.thumbAsset.setAsDefault(thumb_id)

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


