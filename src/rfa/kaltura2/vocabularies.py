
"""functions for populating vocabularies for various select or multiselect fields"""
from zope.interface import provider, implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from rfa.kaltura2.controlpanel import IRfaKalturaSettings
from rfa.kaltura2.kutils import GetVideoPlayers
from rfa.kaltura2.kutils import GetCategories, GetCategoryId
 
@provider(IContextSourceBinder)
def getTagVocabulary():
    """Get Currently created tags on Kaltura server"""
    # Not implemented yet.
    pass

@implementer(IContextSourceBinder)
class CategoryVocabularyFactory(object):
    
    def __init__(self, parent=None):
        """Parent must be a category ID from Kaltura, not a name"""
        self.parent = parent
        self.vocab = None
        
    def __call__(self, context):        
        """Get Currently created Categories on Kaltura server"""
        if self.vocab is None: #no cache, get category list
            items = []
            if self.parent is None:
                #check settings for 'top level category'
                registry = getUtility(IRegistry)
                settings = registry.forInterface(IRfaKalturaSettings)
                tlc = settings.topLevelCategory
                if tlc:
                    parentCategoryId = GetCategoryId(categoryName=tlc)
                    #place the top-level category at the top of the list, so it's selectable.
                    items.append( SimpleTerm(str(parentCategoryId), str(parentCategoryId),tlc,) )
                else:
                    self.parentCateogyId = None #all categories
            
            if self.parent == 'All':
                self.parentCategoryId = None #all categories
                
            categoryObjs = GetCategories(parentCategoryId)
            for cat in categoryObjs:
                #simple term takes value, token, title
                items.append( SimpleTerm(str(cat.getId()), 
                                         str(cat.getId()), 
                                         cat.getName()) 
                              )
            
            self.vocab = SimpleVocabulary(items)
            
        return self.vocab


@provider(IContextSourceBinder)
def VideoPlayerVocabularyFactory(context):
    players = GetVideoPlayers()
        
    items = []
    for player in players:
        name = player.getName()
        items.append( (name, str(player.getId())) )
        
    return SimpleVocabulary.fromItems(items)


@provider(IContextSourceBinder)
def PlaylistPlayerVocabularyFactory(context):
    players = GetPlaylistPlayers()
        
    items = []
    for player in players:
        #simpleVocabulary doesn't like unicode!
        name = player.getName()
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        items.append( (name, str(player.getId())) )
        
    return SimpleVocabulary.fromItems(items)