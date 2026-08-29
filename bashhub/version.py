import platform

try:
    from ._version import __version__
except ImportError:
    # Source checkouts do not contain the build-generated version module.
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)

version_str = 'Bashhub {0} (python {1})'.format(__version__, platform.python_version())
