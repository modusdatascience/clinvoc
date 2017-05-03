
from ._version import get_versions
__version__ = get_versions()['version']
__clean__ = not get_versions()['dirty']
del get_versions
