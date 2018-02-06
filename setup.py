from distutils.core import setup
setup(
  name = 'django-orml',
  packages = ['orml'],
  version = '0.1.1',
  description = 'Django Object Relational Mapping Language',
  author = 'Matt Roberts',
  author_email = 'contact@maleero.com',
  url = 'https://github.com/malero/django-orml',
  download_url = 'https://github.com/malero/django-orml/archive/v0.1.1.tar.gz',
  keywords = ['django', 'orm', 'ply'],
  classifiers = [],
  install_requires=['ply==3.10',],
)
