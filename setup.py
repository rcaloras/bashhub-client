from setuptools import setup, find_packages
from bashhub.version import __version__ as version

tests_require = ['pytest>=3.3.1']

setup(name='bashhub',
      version=version,
      description='Bashhub.com python client',
      url='https://github.com/rcaloras/bashhub-client',
      author='Ryan Caloras',
      author_email='ryan@bashhub.com',
      license='Apache',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: 3.14',
      ],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'requests>=2.33.1', 'jsonpickle>=4.1.1', 'click>=8.3.2',
          'npyscreen>=5.0.2', 'python-dateutil>=2.9.0.post0',
          'inflection>=0.5.1', 'humanize>=4.15.0'
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': ['bh=bashhub.bh:main',
                              'bashhub=bashhub.bashhub:main']
      },
      zip_safe=False)
