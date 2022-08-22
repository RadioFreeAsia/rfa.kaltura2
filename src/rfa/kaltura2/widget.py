from zope.interface import implementer_only
from plone.formwidget.namedfile.widget import NamedFileWidget

from rfa.kaltura2.interfaces import IUploadFileWidget


@implementer_only(IUploadFileWidget)
class FileUploadWidget(NamedFileWidget):
    def update(self):
        super(FileUploadWidget, self).update()

