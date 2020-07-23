from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from rfa.kaltura2.controlpanel import IRfaKalturaSettings

from plone.dexterity.browser.view import DefaultView
class KalturaVideoView(DefaultView):
    
    def getPlaybackUrl(self):
        return None #XXX TODO
    
    def partnerId(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRfaKalturaSettings)
        return settings.partnerId
    
    def playerId(self):
        return self.context.player
    
    def entryId(self):
        try:
            return self.context.KalturaObject.getId()
        except AttributeError: #No KalturaObject for some reason
            return self.context.entryId
    
    
