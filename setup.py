from setuptools import setup
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
        orig_run(self)
        install_bashhub.main()

    command_subclass.run = modified_run
    return command_subclass

@postinstall
class BashhubInstall(install):
    pass

@postinstall
class BashhubDevelop(develop):
    pass


setup(name='bashhub',
        version='0.0.1',
        description='Bashhub.com python client',
        url='http://github.com/rcaloras',
        author='Ryan Caloras',
        author_email='ryan@bashhub.com',
        license='MIT',
        packages=['bashhub'],
        include_package_data=True,
        install_requires=[
            'requests==1.2.3',
            'jsonpickle==0.7.0',
            'pyCLI==2.0.3',
            'pymongo==2.6'],
        entry_points={
            'console_scripts':['bashhub-bh=bashhub.bh:main']
            },
        cmdclass={
            'install': BashhubInstall,
            'develop': BashhubDevelop
            },
        zip_safe=False)
