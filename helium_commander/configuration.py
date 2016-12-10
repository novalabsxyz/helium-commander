from __future__ import unicode_literals
from helium import Configuration, DeviceConfiguration
from future.utils import iteritems

def display_map(cls, client, include=None):
    def _count_dev_configs(self):
        return len(self.device_configurations(use_included=True))

    def _attributes(self):
        return {k: v for k, v in iteritems(vars(self))
                if not (k.startswith('_') or k == 'id')}

    dict = super(Configuration, cls).display_map(client, include=include)

    if include and DeviceConfiguration in include:
        dict['devices'] = _count_dev_configs

    dict.update([
        ('attributes', _attributes),
    ])
    return dict


Configuration.display_map = classmethod(display_map)
