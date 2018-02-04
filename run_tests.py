import dj_database_url
import django, sys
import os
from django.conf import settings

DIRNAME = os.path.dirname(__file__)

DATABASE_URL = os.environ.get('DATABSE_URL', None)
if DATABASE_URL is None:
    DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': os.path.join(DIRNAME, 'database.db'),
                    }
                }
else:
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

settings.configure(DEBUG=True,
               DATABASES=DATABASES,
               INSTALLED_APPS=('django.contrib.auth',
                              'django.contrib.contenttypes',
                              'orml',
                              'orml.tests',
               ))

try:
    # Django <= 1.8
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    # Django >= 1.8
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['orml'])
if failures:
    sys.exit(failures)
