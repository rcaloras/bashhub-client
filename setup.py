from setuptools import setup, find_packages
import install_bashhub
from bashhub.version import __version__ as version

exec (open('bashhub/version.py').read())

tests_require = ['pytest>=3.3.1']

setup(name='bashhub',
      version=version,
      description='Bashhub.com python client',
      url='https://github.com/rcaloras/bashhub-client',
      author='Ryan Caloras',
      author_email='ryan@bashhub.com',
      license='Apache',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'requests==2.32.5', 'jsonpickle==3.0.1', 'click==6.7',
          'npyscreen==4.10.5', 'python-dateutil==2.8.1',
          'inflection==0.3.1', 'humanize==4.6.0',
          'future==0.18.3', 'mock==3.0.5'
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': ['bh=bashhub.bh:main',
                              'bashhub=bashhub.bashhub:main']
      },
      zip_safe=False)
