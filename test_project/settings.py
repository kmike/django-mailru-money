# Django settings for test_project project.
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
join = lambda p: os.path.abspath(os.path.join(PROJECT_ROOT, p))

sys.path.insert(0, join('..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ':MEMORY:',                      # Or path to database file if using sqlite3.
    }
}

USE_TZ = True
ROOT_URLCONF = 'urls'

SECRET_KEY = 'mmq7j3kr3a0@^%qx4m*tmt30tbt24#^zmai_ba!1@_*j+_4z5a'
INSTALLED_APPS = ['mailru_money', 'test_app',
                  'django.contrib.auth', 'django.contrib.contenttypes']

# south doesn't support python 3
try:
    import south
    INSTALLED_APPS.append('south')
except ImportError:
    pass

MAILRU_MONEY_SHOP_ID = 'shop-id'
MAILRU_MONEY_SECRET_KEY = 'secret-key'
