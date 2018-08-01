# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

TWO_FACTOR_AVAILABLE_METHODS = getattr(
    settings,
    'TWO_FACTOR_AVAILABLE_METHODS',
    (
        ('generator', _('Token generator')),
        ('yubikey', _('YubiKey')),
        ('cac', _('Common Access Card (CAC)')),
    ))

# This is the error message the X509 methods display when there is no
# certificate information that is received from the browser.
TWO_FACTOR_NO_CERT_MESSAGE = getattr(
    settings,
    'TWO_FACTOR_NO_CERT_MESSAGE',
    'We did not get any certificate information for your two-factor CAC '
    'login. Please verify that your CAC is inserted into your reader and '
    'your user certificate is loaded in your browser.')

# This is the error message the X509 methods display when there is
# non-matching certificate information that is received from the browser.
TWO_FACTOR_WRONG_CERT_MESSAGE = getattr(
    settings,
    'TWO_FACTOR_WRONG_CERT_MESSAGE',
    'We did not get the correct certificate information for your two-factor '
    'CAC login. Please verify that you are using the correct CAC and your '
    'user certificate is loaded in your browser.')
