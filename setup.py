from setuptools import setup

setup(name='bashhub',
      version='0.0.1',
      description='Bashhub.com python client',
      url='http://github.com/rcaloras',
      author='Ryan Caloras',
      author_email='ryan@bashhub.com',
      license='MIT',
      packages=['bashhub'],
      install_requires=[
          'requests==1.2.3',
          'jsonpickle==0.5.0',
          'pyCLI==2.0.3',
          'pymongo==2.6'],
      entry_points = {
                  'console_scripts':['bashhub-bh=bashhub.bh:main']
      },
      zip_safe=False)
