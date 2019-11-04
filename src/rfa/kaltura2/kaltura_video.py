from rfa.kaltura2 import _
from plone.supermodel import model
from zope import schema
from plone.namedfile.field import NamedFile

class IKaltura_Video(model.Schema):
    
    title = schema.TextLine(
        title=_('video name')
    )
    
    description = schema.Text(
        title=_('video summary'),
    )
    
    player = schema.Choice(
        #TODO
        )
    
    categories = schema.Choice(
        #TODO
    )
    
    tags = schema.List(
    )
    
    file = NamedFile