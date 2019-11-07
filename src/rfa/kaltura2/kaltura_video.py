from plone.autoform import directives
from plone.supermodel import model
from zope import schema
from plone.namedfile.field import NamedFile

from rfa.kaltura2.vocabularies import VideoPlayerVocabularyFactory
from rfa.kaltura2.vocabularies import CategoryVocabularyFactory
from rfa.kaltura2.vocabularies import getTagVocabulary

from rfa.kaltura2 import _

class IKaltura_Video(model.Schema):
    
    title = schema.TextLine(
        title=_('video name'),
        description=_('The short name of this video')
    )
    
    description = schema.Text(
        title=_('video summary'),
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
    
    tags = schema.List(
        title=_('Tags'),
        description=_("keyword tag(s) associated with this video (one per line)"),
        value_type=schema.Text()
    )
    
    video_file = NamedFile(
        title=_('video file'),
    )
    
    directives.omitted('entryId') #User never interacts with this field
    entryId = schema.Text(
        title=_('entryid'),
        description=_('Entry Id set by Kaltura after upload (read only)'),
        default=None
    )
    