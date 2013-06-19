import os
from setuptools import setup
from setuptools import find_packages
import sys

VERSION = '0.1dev'

requires = [
    'numpy',
    'matplotlib'
]
tests_require = requires + ['mock']

if sys.version < '2.7':
    tests_require += ['unittest2']

testing_extras = tests_require + ['nose', 'coverage', 'tox']
doc_extras = ['Sphinx']

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

setup(name='ampanal',
      version=VERSION,
      description='Automated Amplifier Analysis Tool',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Database",
        #"License :: Repoze Public License",
        ],
      keywords='',
      author="Chris Rossi",
      author_email="cr@duskyamp.com",
      #url="http://pylonsproject.org",
      #license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
          'testing': testing_extras,
          'docs': doc_extras,
      },
      test_suite="ampanal.tests",
      entry_points="""\
      [console_scripts]
      measure = ampanal.scripts.measure:main
      """)
