import logging
from binascii import unhexlify

from django.conf import settings
from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django_otp.models import Device
from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex
from phonenumber_field.modelfields import PhoneNumberField

from .gateways import make_call, send_sms
from .settings import TWO_FACTOR_AVAILABLE_METHODS

try:
    import yubiotp
except ImportError:
    yubiotp = None


logger = logging.getLogger(__name__)

PHONE_METHODS = (
    ('call', _('Phone Call')),
    ('sms', _('Text Message')),
)


def get_available_phone_methods():
    methods = []
    if getattr(settings, 'TWO_FACTOR_CALL_GATEWAY', None):
        methods.append(('call', _('Phone call')))
    if getattr(settings, 'TWO_FACTOR_SMS_GATEWAY', None):
        methods.append(('sms', _('Text message')))
    return methods


def get_available_yubikey_methods():
    methods = []
    if yubiotp and 'otp_yubikey' in settings.INSTALLED_APPS:
        methods.append(('yubikey', _('YubiKey')))
    return methods

def get_available_x509_methods():
    methods = [('cac', _('Common Access Card (CAC)'))]
    return methods

def get_available_methods():
    return TWO_FACTOR_AVAILABLE_METHODS


def key_validator(*args, **kwargs):
    """Wraps hex_validator generator, to keep makemigrations happy."""
    return hex_validator()(*args, **kwargs)


def random_hex_str(length=20):
    # Could be removed once we depend on django_otp > 0.7.5
    return force_str(random_hex(length=length))


class PhoneDevice(Device):
    """
    Model with phone number and token seed linked to a user.
    """
    class Meta:
        app_label = 'two_factor'

    number = PhoneNumberField()
    key = models.CharField(max_length=40,
                           validators=[key_validator],
                           default=random_hex_str,
                           help_text="Hex-encoded secret key")
    method = models.CharField(max_length=4, choices=PHONE_METHODS,
                              verbose_name=_('method'))

    def __repr__(self):
        return '<PhoneDevice(number={!r}, method={!r}>'.format(
            self.number,
            self.method,
        )

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def verify_token(self, token):
        # local import to avoid circular import
        from two_factor.utils import totp_digits

        try:
            token = int(token)
        except ValueError:
            return False

        for drift in range(-5, 1):
            if totp(self.bin_key, drift=drift, digits=totp_digits()) == token:
                return True
        return False

    def generate_challenge(self):
        # local import to avoid circular import
        from two_factor.utils import totp_digits

        """
        Sends the current TOTP token to `self.number` using `self.method`.
        """
        no_digits = totp_digits()
        token = str(totp(self.bin_key, digits=no_digits)).zfill(no_digits)
        if self.method == 'call':
            make_call(device=self, token=token)
        else:
            send_sms(device=self, token=token)


class X509Device(Device):
    """ 1:M mapping of Users to certificate (X.509) DNs (subjects) """

    class Meta:
        app_label = 'two_factor'

    user = models.ForeignKey(
        User,
        verbose_name="User",
        help_text="Django User associated with certificate.",
        default=None, blank=True, null=True,
        related_name="%(app_label)s_%(class)s_related",)

    cert_dn = models.CharField(
        help_text="Certificate matter to match on.",
        max_length=1024,
        blank=False,
        unique=True)

    def verify_token(self, token):
        return True

    def __str__(self):
        return "{0}:{1}".format(self.user.username, self.cert_dn)
