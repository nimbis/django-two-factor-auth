# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings

from .forms import (MethodForm, PhoneNumberForm, DeviceValidationForm,
    TOTPDeviceForm, YubiKeyDeviceForm, X509DeviceForm)

TWO_FACTOR_ALLOWED_METHODS = getattr(
    settings,
    'TWO_FACTOR_ALLOWED_METHODS',
    (
        ('method', MethodForm),
        ('generator', TOTPDeviceForm),
        ('sms', PhoneNumberForm),
        ('call', PhoneNumberForm),
        ('validation', DeviceValidationForm),
        ('yubikey', YubiKeyDeviceForm),
        ('cac', X509DeviceForm),
    ))
