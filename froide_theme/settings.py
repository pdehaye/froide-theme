# -*- coding: utf-8 -*-
import os
import re

from froide.settings import Base, ThemeBase, HerokuPostmark, HerokuPostmarkS3, Production as ProductionFroide # noqa

THEME_ROOT = os.path.abspath(os.path.dirname(__file__))
rec = lambda x: re.compile(x, re.I | re.U)

class CustomThemeBase(ThemeBase, Base):
    gettext = lambda s:s
    LANGUAGES = (('de-at', gettext('German'),),)
    FROIDE_THEME = 'froide_theme.theme'
    LANGUAGE_CODE = 'de_AT'

    EMAIL_SUBJECT_PREFIX = '[FDS-Admin] ' # for mail_admins

    CUSTOM_AUTH_USER_MODEL_DB = 'auth_user'

    SITE_NAME = "Frag Den Staat"
    SITE_EMAIL = "info@fragdenstaat.at"
    SITE_URL = 'https://fragdenstaat.at'

    SECRET_URLS = {
        "admin": "admin",
    }

    STATIC_ROOT = os.path.abspath(os.path.join(THEME_ROOT, '..', 'public'))
    MEDIA_ROOT = os.path.abspath(os.path.join(THEME_ROOT, "..", "files"))

    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

    CELERY_EMAIL_TASK_CONFIG = {
        'max_retries': None,
        'ignore_result': False,
        'acks_late': True,
        'store_errors_even_if_ignored': True
    }

    HAYSTACK_CONNECTIONS = {
       'default': {
           'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
           'PATH': os.path.abspath(os.path.join(THEME_ROOT, '..', 'whoosh_index')),
           'STORAGE': 'file',
           'INCLUDE_SPELLING': False,
           'BATCH_SIZE': 100,
       }
    }
    HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'fragdenstaat',                      # Or path to database file if using sqlite3.
            'USER': 'fragdenstaat',                      # Not used with sqlite3.
            # PASSWORD IS SET IN local_settings
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_AGE = 3628800             # six weeks for usability
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True


    DEFAULT_FROM_EMAIL = SITE_EMAIL


    EMAIL_HOST = "localhost"
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "foi"
    EMAIL_USE_TLS = False
    # EMAIL_HOST_PASSWORD given in local_settings.py

    FOI_EMAIL_HOST_IMAP = EMAIL_HOST
    FOI_EMAIL_PORT_IMAP = 143
    FOI_EMAIL_ACCOUNT_NAME = EMAIL_HOST_USER
    FOI_EMAIL_DOMAIN = "foi.fragdenstaat.at"
    FOI_EMAIL_USE_SSL = False
    # FOI_EMAIL_ACCOUNT_PASSWORD given in local_settings.py

    FOI_EMAIL_HOST = EMAIL_HOST
    FOI_EMAIL_PORT = EMAIL_PORT
    FOI_EMAIL_FIXED_FROM_ADDRESS = False
    FOI_EMAIL_HOST_USER = FOI_EMAIL_ACCOUNT_NAME
    FOI_EMAIL_USE_TLS = False
    # FOI_EMAIL_HOST_PASSWORD given in local_settings.py

    @property
    def LOCALE_PATHS(self):
        return [
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', "locale")
            )
        ] + list(super(CustomThemeBase, self).LOCALE_PATHS.default)

    @property
    def INSTALLED_APPS(self):
        return super(CustomThemeBase, self).INSTALLED_APPS + ['gunicorn','celery_haystack','djcelery_email']

    @property
    def MIDDLEWARE_CLASSES(self):
        mc = super(CustomThemeBase, self).MIDDLEWARE_CLASSES
        mc = [x for x in mc if 'Locale' not in x]
        mc.insert(mc.index('django.middleware.common.CommonMiddleware') or 0, 'djangosecure.middleware.SecurityMiddleware')
        return mc + ['django.contrib.flatpages.middleware.FlatpageFallbackMiddleware']

    @property
    def FROIDE_CONFIG(self):
        config = super(CustomThemeBase, self).FROIDE_CONFIG
        config.update(dict(
            create_new_publicbody=False,
            publicbody_empty=False,
            user_can_hide_web=True,
            public_body_officials_public=False,
            public_body_officials_email_public=False,
            default_law=1,
            doc_conversion_binary="/usr/bin/libreoffice",
            dryrun=False,
            payment_possible=False,
            dryrun_domain="test.fragdenstaat.at",
            allow_pseudonym=True,
            api_activated=True,
            search_engine_query='http://www.google.de/search?as_q=%(query)s&as_epq=&as_oq=&as_eq=&hl=en&lr=&cr=&as_ft=i&as_filetype=&as_qdr=all&as_occt=any&as_dt=i&as_sitesearch=%(domain)s&as_rights=&safe=images',
            show_public_body_employee_name=False,
            greetings=[rec(u"Sehr geehrt(er? (?:Herr|Frau)(?: ?Dr\.?)?(?: ?Prof\.?)? .*)")],
            closings=[rec(u"[Mm]it( den)? (freundlichen|vielen|besten) Gr\xfc\xdfen,?"), rec("Hochachtungsvoll,?"), rec('i\. ?A\.'), rec('[iI]m Auftrag')]
        ))
        return config



class DevBase(CustomThemeBase):
    DEBUG = True
    EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'

    @property
    def FROIDE_CONFIG(self):
        config = super(DevBase, self).FROIDE_CONFIG
        config.update(dict(
            dryrun=True,
            dryrun_domain="test.fragdenstaat.at"
        ))
        return config


class ProductionBase(CustomThemeBase, ProductionFroide):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }


class ThemeHerokuPostmark(CustomThemeBase, HerokuPostmark):
    pass


class ThemeHerokuPostmarkS3(CustomThemeBase, HerokuPostmarkS3):
    pass


try:
    from .local_settings import *  # noqa
except ImportError, e:
    print 'ERROR', e
    pass
