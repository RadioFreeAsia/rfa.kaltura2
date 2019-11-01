# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import rfa.kaltura2


class RfaKaltura2Layer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rfa.kaltura2)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'rfa.kaltura2:default')


RFA_KALTURA2_FIXTURE = RfaKaltura2Layer()


RFA_KALTURA2_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RFA_KALTURA2_FIXTURE,),
    name='RfaKaltura2Layer:IntegrationTesting',
)


RFA_KALTURA2_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RFA_KALTURA2_FIXTURE,),
    name='RfaKaltura2Layer:FunctionalTesting',
)


RFA_KALTURA2_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        RFA_KALTURA2_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='RfaKaltura2Layer:AcceptanceTesting',
)
