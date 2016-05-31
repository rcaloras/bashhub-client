from setuptools import setup, find_packages
import install_bashhub
import sys

exec (open('bashhub/version.py').read())

setup(name='bashhub',
      version='__version__',
      description='Bashhub.com python client',
      url='https://github.com/rcaloras/bashhub-client',
      author='Ryan Caloras',
      author_email='ryan@bashhub.com',
      license='Apache',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'requests==1.2.3', 'jsonpickle==0.7.0', 'click==3.3',
          'npyscreen==4.9.1', 'python-dateutil==2.4', 'pyCLI==2.0.3',
          'pymongo==2.6', 'inflection==0.2.1', 'humanize==0.5.1'
      ],
      entry_points={
          'console_scripts': ['bh=bashhub.bh:main',
                              'bashhub=bashhub.bashhub:main']
      },
      zip_safe=False)
