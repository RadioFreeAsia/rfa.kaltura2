from zope.interface import Interface
from zope.interface import implementer
from zope.interface import directlyProvides

from KalturaClient.Plugins.Core import KalturaMediaEntry
from KalturaClient.Plugins.Core import KalturaMediaType

from rfa.kaltura2.interfaces import IKalturaMediaEntry

class IKalturaMediaEntryProvider(Interface):
    
    def getEntry(self):
        """Returns a KalturaMediaEntry representing the plone context 
           KalturaVideo
        
           This effectively can turn our KalturaVideo schema 
           into a KalturaMediaEntry for the Kaltura API"""



@implementer(IKalturaMediaEntryProvider)
class Kaltura_VideoMediaEntryProvider(object): 
    
    def __init__(self, context):
        
        self.mediaEntry = KalturaMediaEntry()
        directlyProvides(self.mediaEntry, IKalturaMediaEntry)
        
        self.mediaEntry.setMediaType(KalturaMediaType(KalturaMediaType.VIDEO))
        self.mediaEntry.setReferenceId(context.UID())
        
        self.mediaEntry.setName(context.title)
        
        #set Description
        self.mediaEntry.setDescription(context.description)
        #Set Tags
        self.mediaEntry.setTags(context.tags)
        
        #Don't set categories - those are handled separately.    
            
    def getEntry(self):
        return self.mediaEntry
    