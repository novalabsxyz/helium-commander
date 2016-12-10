from __future__ import unicode_literals

from helium import Device, Configuration, DeviceConfiguration


def display_map(cls, client, uuid=False, include=None):
    def _trim_id(res):
        return res.id if uuid or client.uuid else res.short_id

    def _config(self):
        return _trim_id(self.configuration(use_included=True))

    def _device(self):
        return _trim_id(self.device(use_included=True))

    def _device_type(self):
        return self.device(use_included=True)._resource_type()

    def _loaded(self):
        return 'yes' if self.is_loaded else 'no'

    dict = super(DeviceConfiguration, cls).display_map(client, include=include)
    if include and Configuration in include:
        dict['config'] = _config
    if include and Device in include:
        dict['device'] = _device
        dict['type'] = _device_type

    dict['loaded'] = _loaded

    return dict


DeviceConfiguration.display_map = classmethod(display_map)
