from plone.autoform import directives
from plone.supermodel import model
from zope import schema
from zope.interface import Interface

from plone.namedfile.field import NamedFile, NamedBlobFile

from plone.app.z3cform.widget import AjaxSelectFieldWidget

from rfa.kaltura2.interfaces import IKalturaMediaEntry

from rfa.kaltura2.vocabularies import VideoPlayerVocabularyFactory
from rfa.kaltura2.vocabularies import CategoryVocabularyFactory
from rfa.kaltura2.vocabularies import getTagVocabulary
from collective import dexteritytextindexer

from rfa.kaltura2 import _


class IKaltura_Video(model.Schema):

    title = schema.TextLine(
        title=_('Video Title'),
        description=_('Title of your video')
    )

    description = schema.Text(
        title=_('Video summary'),
    )

    player = schema.Choice(
        title=_('Player'),
        description=_('Choose the player to use'),
        source=VideoPlayerVocabularyFactory
        )

    categories = schema.List(
        title=_('Categories'),
        description=_("Select video category(ies) this video belongs in"),
        value_type=schema.Choice(source=CategoryVocabularyFactory(None))
    )
    dexteritytextindexer.searchable('tags')
    tags = schema.Tuple(
        title=_('Tags'),
        description=_("keyword tag(s) associated with this video (one per line)"),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'tags',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Keywords'
    )

    video_file = NamedBlobFile(
        title=_('video file'),
    )
    model.primary('video_file')
    ##Hidden Fields
    #User never interacts with these fields
    directives.omitted('entryId', 'KalturaObject')
    entryId = schema.Text(
        title=_('entryid'),
        description=_('Entry Id set by Kaltura after upload (read only)'),
        default=None
    )

    #This stores the python object representing the entry in the Kaltura Media Center
    KalturaObject = schema.Object(IKalturaMediaEntry)


