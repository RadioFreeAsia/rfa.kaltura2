# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from rfa.kaltura2.testing import RFA_KALTURA2_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that rfa.kaltura2 is properly installed."""

    layer = RFA_KALTURA2_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if rfa.kaltura2 is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'rfa.kaltura2'))

    def test_browserlayer(self):
        """Test that IRfaKaltura2Layer is registered."""
        from rfa.kaltura2.interfaces import (
            IRfaKaltura2Layer)
        from plone.browserlayer import utils
        self.assertIn(
            IRfaKaltura2Layer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = RFA_KALTURA2_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['rfa.kaltura2'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if rfa.kaltura2 is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'rfa.kaltura2'))

    def test_browserlayer_removed(self):
        """Test that IRfaKaltura2Layer is removed."""
        from rfa.kaltura2.interfaces import \
            IRfaKaltura2Layer
        from plone.browserlayer import utils
        self.assertNotIn(
            IRfaKaltura2Layer,
            utils.registered_layers())
