# -*- coding: utf-8 -*-
from zope.interface import Interface

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IRfaKaltura2Layer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IKalturaMediaEntry(Interface):
    """A KalturaMediaEntry object defined by KalturaClient
       This represents an instance of KaltraClient.Plugins.Core.KalturaMediaEntry
    """