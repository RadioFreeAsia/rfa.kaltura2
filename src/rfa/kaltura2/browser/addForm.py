from bdb import set_trace
from plone.dexterity.browser import add
from Products.CMFPlone.resources import add_resource_on_request

class AddForm(add.DefaultAddForm):
    portal_type = 'Kaltura Video'

    def update(self):
        return super(AddForm, self).update()

class AddView(add.DefaultAddView):
    form = AddForm

    def __call__(self):
        add_resource_on_request(self.request, 'filepond')
        # add_resource_on_request(self.request, 'filepondesm')
        add_resource_on_request(self.request, 'kalturaFileUploader')

        return super(AddView, self).__call__()
