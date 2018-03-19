from distutils.core import setup
from pkgutil import walk_packages

import orml


def find_packages(path, prefix=""):
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


setup(
  name = 'django-orml',
  packages = list(find_packages(orml.__path__, orml.__name__)),
  version = '0.1.6',
  description = 'Django Object Relational Mapping Language',
  author = 'Matt Roberts',
  author_email = 'contact@maleero.com',
  url = 'https://github.com/malero/django-orml',
  download_url = 'https://github.com/malero/django-orml/archive/v0.1.1.tar.gz',
  keywords = ['django', 'orm', 'ply'],
  classifiers = [],
  install_requires=['ply==3.10',],
)
