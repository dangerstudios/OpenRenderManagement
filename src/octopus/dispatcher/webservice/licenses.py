'''
Created on Apr 27, 2012

@author: Arnaud Chassagne
'''

from octopus.core.framework import ResourceNotFoundError
from octopus.dispatcher.webservice import DispatcherBaseResource
from octopus.core.communication.http import Http404, Http500
try:
    import simplejson as json
except ImportError:
    import json

class LicensesResource(DispatcherBaseResource):
    #@queue
    def get(self):
        lic_data = {}
        for name, lic in self.dispatcher.licenseManager.licenses.iteritems():
            lic_data[name] = {"max": lic.maximum, "used": lic.used, "rns":
                [rn.name for rn in sorted(lic.currentUsingRenderNodes)]}
        self.writeCallback(json.dumps(lic_data))


class LicenseResource(DispatcherBaseResource):
    #@queue
    def get(self, licenseName):
        try:
            lic = self.dispatcher.licenseManager.licenses[licenseName]
            lic_data = {"max": lic.maximum, "used": lic.used, "rns":
                [rn.name for rn in sorted(lic.currentUsingRenderNodes)]}
            self.writeCallback(json.dumps(lic_data))
        except KeyError:
            raise ResourceNotFoundError

    #@queue
    def put(self, licenseName):
        data = self.getBodyAsJSON()
        try:
            maxLic = data['maxlic']
        except KeyError:
            raise Http404("Missing entry : 'maxlic'")
        else:
            self.dispatcher.licenseManager.setMaxLicensesNumber(licenseName, maxLic)
            self.writeCallback("OK")

    #@queue
    def delete(self, licenseName):
        data = self.getBodyAsJSON()
        try:
            rns = data['rns']
        except KeyError:
            raise Http404("Missing entry : 'rns'")
        else:
            rnsList = rns.split(",")
            for rnName in rnsList:
                if rnName in self.dispatcher.dispatchTree.renderNodes:
                    rn = self.dispatcher.dispatchTree.renderNodes[rnName]
                else:
                    raise Http500("Internal Server Error: Render node %s is not registered." % (rnName))

                self.dispatcher.licenseManager.releaseLicenseForRenderNode(licenseName, rn)
            self.writeCallback("OK")
