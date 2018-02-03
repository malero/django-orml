import django, sys
from django.conf import settings

settings.configure(DEBUG=True,
               DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                    }
                },
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
