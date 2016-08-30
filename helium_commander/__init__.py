from .__about__ import (
    __package_name__, __title__, __author__, __author_email__,
    __license__, __copyright__, __version__, __revision__,
    __url__,
)
from .resource import Resource, ResourceMeta
from .sensor import Sensor
from .client import Client

__all__ = (
    Resource, ResourceMeta,
    Sensor,
    Client,
    # Metadata attributes
    '__package_name__',
    '__title__',
    '__author__',
    '__author_email__',
    '__license__',
    '__copyright__',
    '__version__',
    '__revision__',
    '__url__',
)
