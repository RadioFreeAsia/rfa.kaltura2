from rfa.kaltura2 import _
from plone.supermodel import model
from zope import schema
from plone.namedfile.field import NamedFile


class IKaltura_Video(model.Schema):
    
    title = schema.TextLine(
        title=_('video name'),
        description=_('The short name of this video')
    )
    
    description = schema.Text(
        title=_('video summary'),
    )
    
    entryId = schema.Text(
        title=_('entryid'),
        description=_('Entry Id set by Kaltura after upload (read only)'))
    
    player = schema.Choice(
        title=_('Player'),
        description=_('Choose the player to use'),
        source=PlayerVocabularyFactory
        )
    
    categories = schema.List(
        title=_('Categories'),
        description=_("Select video category(ies) this video belongs in"),
        value_type=schema.Choice(source=getCategoryVocabulary)
    )
    
    tags = schema.List(
        title=_('Tags'),
        description=_("keyword tag(s) associated with this video (one per line)"),
        value_type=schema.Text()
    )
    
    video_file = NamedFile(
        title=_('video file'),
    )
    
"""functions for populating vocabularies for various select or multiselect fields"""
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from rfa.kaltura2.controlpanel import IRfaKalturaSettings
from rfa.kaltura2.kutils import kGetVideoPlayers
from rfa.kaltura2.kutils import kGetCategories, kGetCategoryId
 
@provider(IContextSourceBinder)
def getTagVocabulary():
    """Get Currently created tags on Kaltura server"""
    # Not implemented yet.
    pass

@provider(IContextSourceBinder)
def getCategoryVocabulary(parent=None):
    """Get Currently created Categories on Kaltura server"""
    
    items = []
    if parent is None:
        #check settings for 'top level category'
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRfaKalturaSettings)
        tlc = settings.topLevelCategory
        if tlc:
            parent = kGetCategoryId(categoryName=tlc)
            #place the top-level category at the top of the list, so it's selectable.
            items.append( (str(parent), tlc,) )
        
    categoryObjs = kGetCategories(parent)
    for cat in categoryObjs:
        items.append( (str(cat.getId()), cat.getName(),) )
        
    return items


@provider(IContextSourceBinder)
def PlayerVocabularyFactory(context):
    players=[]
    players = kGetVideoPlayers()
        
    items = []
    for player in players:
        #simpleVocabulary doesn't like unicode!
        name = player.getName()
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        items.append( (name, str(player.getId())) )
        
    return SimpleVocabulary.fromItems(items)
