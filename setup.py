from setuptools import setup, find_packages
import install_bashhub
from bashhub.version import __version__

tests_require = ['pytest>=3.3.1']

setup(name='bashhub',
      version=__version__,
      description='Bashhub.com python client',
      url='https://github.com/rcaloras/bashhub-client',
      author='Ryan Caloras',
      author_email='ryan@bashhub.com',
      license='Apache',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'requests==2.23.0', 'jsonpickle==2.0.0', 'click==6.7',
          'npyscreen==4.10.5', 'python-dateutil==2.8.1',
          'pymongo==3.10.1', 'inflection==0.3.1', 'humanize==1.0.0',
          'future==0.18.2', 'mock==3.0.5'
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': ['bh=bashhub.bh:main',
                              'bashhub=bashhub.bashhub:main']
      },
      zip_safe=False)
