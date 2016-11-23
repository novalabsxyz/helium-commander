from __future__ import unicode_literals
from helium import Metadata
from future.utils import iteritems


def display_map(cls, client, include=None):
    def _attributes(self):
        return {k: v for k, v in iteritems(vars(self))
                if not (k.startswith('_') or k == 'id')}

    dict = super(Metadata, cls).display_map(client, include=include)
    dict.update([
        ('attributes', _attributes),
    ])
    return dict

Metadata.display_map = classmethod(display_map)
