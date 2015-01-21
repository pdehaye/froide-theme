# -*- coding: utf-8 -*-
import os

from froide.settings import Base, ThemeBase, HerokuPostmark, HerokuPostmarkS3  # noqa

THEME_ROOT = os.path.abspath(os.path.dirname(__file__))

class CustomThemeBase(ThemeBase):
    gettext = lambda s:s
    LANGUAGES = (('de-at', gettext('German'),),)
    FROIDE_THEME = 'froide_theme.theme'
    LANGUAGE_CODE = 'de_AT'

    EMAIL_SUBJECT_PREFIX = '[FDS-Admin] ' # for mail_admins

    CUSTOM_AUTH_USER_MODEL_DB = 'auth_user'

    SITE_NAME = "Frag Den Staat"
    SITE_EMAIL = "info@fragdenstaat.at"
    SITE_URL = 'http://localhost:8000'

    SECRET_URLS = {
        "admin": "admin",
    }

    STATIC_ROOT = os.path.abspath(os.path.join(THEME_ROOT, '..', 'public'))

    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

    CELERY_EMAIL_TASK_CONFIG = {
        'max_retries': None,
        'ignore_result': False,
        'acks_late': True,
        'store_errors_even_if_ignored': True
    }


    @property
    def LOCALE_PATHS(self):
        #return list(super(CustomThemeBase, self).LOCALE_PATHS.default) + [
        return [
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', "locale")
            )
        ] # + list(super(CustomThemeBase, self).LOCALE_PATHS.default)

    @property
    def INSTALLED_APPS(self):
        return super(CustomThemeBase, self).INSTALLED_APPS + ['django_gunicorn']

    @property
    def MIDDLEWARE_CLASSES(self):
        mc = super(CustomThemeBase, self).MIDDLEWARE_CLASSES
        mc = [x for x in mc if 'Locale' not in x]
        return mc + ['django.contrib.flatpages.middleware.FlatpageFallbackMiddleware']

    @property
    def FROIDE_CONFIG(self):
        config = super(FragDenStaatBase, self).FROIDE_CONFIG
        config.update(dict(
            create_new_publicbody=False,
            publicbody_empty=True,
            user_can_hide_web=True,
            public_body_officials_public=True,
            public_body_officials_email_public=False,
            default_law=1,
            doc_conversion_binary="/usr/bin/libreoffice",
            dryrun=False,
            dryrun_domain="test.fragdenstaat.at",
            allow_pseudonym=True,
            api_activated=True,
            search_engine_query='http://www.google.de/search?as_q=%(query)s&as_epq=&as_oq=&as_eq=&hl=en&lr=&cr=&as_ft=i&as_filetype=&as_qdr=all&as_occt=any&as_dt=i&as_sitesearch=%(domain)s&as_rights=&safe=images',
            show_public_body_employee_name=False,
            greetings=[rec(u"Sehr geehrt(er? (?:Herr|Frau)(?: ?Dr\.?)?(?: ?Prof\.?)? .*)")],
            closings=[rec(u"[Mm]it( den)? (freundlichen|vielen|besten) Gr\xfc\xdfen,?"), rec("Hochachtungsvoll,?"), rec('i\. ?A\.'), rec('[iI]m Auftrag')]
        ))
        return config



class Dev(CustomThemeBase, Base):
    DEBUG = True
    EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'

    @property
    def FROIDE_CONFIG(self):
        config = super(CustomThemeBase, self).FROIDE_CONFIG
        config.update(dict(
            dryrun=True,
            dryrun_domain="test.fragdenstaat.at"
        ))
        return config


class ThemeHerokuPostmark(CustomThemeBase, HerokuPostmark):
    pass


class ThemeHerokuPostmarkS3(CustomThemeBase, HerokuPostmarkS3):
    pass


try:
    from .local_settings import *  # noqa
except ImportError, e:
    print 'ERROR', e
    pass
