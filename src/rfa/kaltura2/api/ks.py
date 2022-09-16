import json

from Products.Five.browser import BrowserView
from rfa.kaltura2.kutils import kconnect


class getKs(BrowserView):

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        (client, ks) = kconnect()

        response = dict()

        #here, we are assuming that all kaltura session strings are ascii
        response['ks'] = ks.decode()

        return json.dumps(response)


