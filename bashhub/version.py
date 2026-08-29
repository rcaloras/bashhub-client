import platform
from importlib.metadata import version as installed_version

try:
    from ._version import __version__
except ImportError:
    # Editable installs load this source module without the wheel's generated file.
    __version__ = installed_version("bashhub")

version_str = 'Bashhub {0} (python {1})'.format(__version__, platform.python_version())
