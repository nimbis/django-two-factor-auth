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
