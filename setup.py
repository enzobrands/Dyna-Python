#!/usr/bin/env python3

import sys
from distutils.core import setup

if sys.version_info < (3,6):
    sys.exit('Sorry, Python < 3.6 is not supported')

setup(name='Dynizer',
      version='0.1',
      description='Utilities to work with the Dynactionize Dynizer',
      author='Dynactionize NV',
      author_email='info@dynactionize.com',
      url='https://www.dynactionize.com',
      packages=['dynizer'],
      license='Apache License'
)
