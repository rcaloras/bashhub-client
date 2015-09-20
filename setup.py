from setuptools import setup, find_packages
import install_bashhub
import sys
from setuptools.command.install import install
from setuptools.command.develop import develop


def postinstall(command_subclass):
    """A decorator for classes subclassing one of the setuptools commands.

    It modifies the run() method so that it runs our post install setup.
    """
    orig_run = command_subclass.run

    def modified_run(self):
        # Need to run bashhub-setup here
        #
        orig_run(self)

    command_subclass.run = modified_run
    return command_subclass

@postinstall
class BashhubInstall(install):
    pass

@postinstall
class BashhubDevelop(develop):
    pass

exec(open('bashhub/version.py').read())

setup(name='bashhub',
        version='__version__',
        description='Bashhub.com python client',
        url='http://github.com/rcaloras',
        author='Ryan Caloras',
        author_email='ryan@bashhub.com',
        license='MIT',
        packages= find_packages(),
        include_package_data=True,
        install_requires=[
            'requests==1.2.3',
            'jsonpickle==0.7.0',
            'click==3.3',
            'npyscreen==4.9.1',
            'python-dateutil==2.2',
            'pyCLI==2.0.3',
            'pymongo==2.6',
            'inflection==0.2.1',
            'humanize==0.5.1'],
        entry_points={
            'console_scripts':['bh=bashhub.bh:main',
            'bashhub=bashhub.bashhub:main']
            },
        cmdclass={
            'install': BashhubInstall,
            'develop': BashhubDevelop
            },
        zip_safe=False)
