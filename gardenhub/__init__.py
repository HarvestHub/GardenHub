from django.utils.version import get_version

# major.minor.patch.release.number
# release must be one of alpha, beta, rc, or final
VERSION = (1, 1, 0, 'final', 0)

__version__ = get_version(VERSION)
