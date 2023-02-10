from zope.interface import implementer_only
from z3c.form.interfaces import ITextWidget

from rfa.kaltura2.interfaces import IUploadFileWidget


@implementer_only(IUploadFileWidget)
class FileUploadWidget(ITextWidget):
    def update(self):
        super(FileUploadWidget, self).update()

