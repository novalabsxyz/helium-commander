"""Extensions to the base Resource class."""

from __future__ import unicode_literals

from helium import Resource, ResourceMeta
import helium_commander.writer as _writer
import click
from builtins import filter as _filter
from collections import OrderedDict
from contextlib import contextmanager


def filter_mac(id_rep):
    id_rep_lower = id_rep.lower()

    def func(resource):
        try:
            resource_mac = resource.meta.mac
            return resource_mac[-len(id_rep):].lower() == id_rep_lower
        except AttributeError:
            pass
        return False
    return func


def filter_uuid(id_rep):
    def func(resource):
        return resource.id == id_rep
    return func


def filter_short_id(id_rep):
    def func(resource):
        return id_rep == resource.short_id
    return func


def filter_name(id_rep):
    id_rep_lower = None
    id_rep_len = 0
    if id_rep is not None:
        id_rep_lower = id_rep.lower()
        id_rep_len = len(id_rep_lower)

    def func(resource):
        entry_name = resource.name
        if entry_name is None:
            return id_rep_lower is None
        return entry_name[:id_rep_len].lower() == id_rep_lower
    return func


def filter_oneof(lookup_filters):
    def id_func(id_rep):
        resource_filters = [f(id_rep) for f in lookup_filters]

        def func(resource):
            for f in resource_filters:
                if f(resource):
                    return True
            return False
        return func
    return id_func


def filter_id_rep(mac=False):
    if mac:
        filters = [
            filter_mac
        ]
    else:
        filters = [
            filter_uuid,
            filter_short_id,
            filter_name
        ]
    return filter_oneof(filters)


def resource_filter(cls, client, value,
                    lookup_filter=filter_uuid,
                    resources=None,
                    include=None):
    if resources is None:
        resources = cls.all(client, include=include)
    resource_filter = lookup_filter(value)
    return list(_filter(resource_filter, resources))


def resource_lookup(cls, client, id_rep,
                    mac=False,
                    resources=None,
                    include=None):
    resources = resource_filter(cls, client, id_rep,
                                lookup_filter=filter_id_rep(mac=mac),
                                resources=resources,
                                include=include)
    resources_len = len(list(resources)) if resources is not None else 0
    if resources_len == 1:
        return resources[0]
    elif resources_len == 0:
        raise KeyError('Id: {} does not exist'.format(id_rep))
    else:
        ambig_ids = [res.id for res in resources]
        ambig_list = '({})'.format(', '.join(ambig_ids))
        raise KeyError('Ambiguous id: {} {}'.format(id_rep, ambig_list))


Resource.filter = classmethod(resource_filter)
Resource.lookup = classmethod(resource_lookup)
Resource.short_id = property(lambda self: self.id.split('-')[0])


def display_map(cls, client):
    def _id(self):
        return self.id if client.uuid else self.short_id

    return OrderedDict([
        ('id', _id),
    ])


@contextmanager
def display_writer(cls, client, mapping, **kwargs):
    output = kwargs.get('output', client.output)
    output = output or click.utils.get_text_stream('stdout')
    output_format = kwargs.get('format', client.format)
    writer = _writer.for_format(output_format, output)
    writer.start(mapping, **kwargs)
    try:
        yield writer
    finally:
        writer.finish(mapping)


def display_resources(cls, client, resources, **kwargs):
    mapping = cls.display_map(client)
    with cls.display_writer(client, mapping, **kwargs) as writer:
        writer.write_resources(resources, mapping)

Resource.display_writer = classmethod(display_writer)
Resource.display_map = classmethod(display_map)
Resource.display = classmethod(display_resources)
