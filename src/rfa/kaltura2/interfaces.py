# -*- coding: utf-8 -*-
from zope.interface import Interface

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.form.interfaces import ITextWidget

class IRfaKaltura2Layer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IKalturaMediaEntry(Interface):
    """A KalturaMediaEntry object defined by KalturaClient
       This represents an instance of KaltraClient.Plugins.Core.KalturaMediaEntry
    """

class IUploadFileWidget(ITextWidget):
    """
      An IUploadFileWidget is a special NamedFileWidget that uploads
      the file contents to a remote destination instead of saving it as a blob.
      This is a specific implementation for Kaltura's upload api.
    """
