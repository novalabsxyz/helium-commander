"""Extensions to the base Resource class."""

from __future__ import unicode_literals
import helium
from builtins import filter


def filter_mac(id_rep):
    id_rep_lower = id_rep.lower()

    def func(resource):
        resource_mac = resource.meta.mac
        if resource_mac is not None:
            return resource_mac[-len(id_rep):].lower() == id_rep_lower
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
    id_rep_lower = id_rep.lower()
    id_rep_len = len(id_rep_lower)

    def func(resource):
        entry_name = resource.name
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


def lookup_all_matching(cls, client, id_rep, lookup_filter=filter_uuid,
                        resources=None):
    if resources is None:
        resources = cls.all(client)
    resource_filter = lookup_filter(id_rep)
    return list(filter(resource_filter, resources))


def lookup_all_id(cls, client, id_rep, mac=False, resources=None):
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
    lookup_filter = filter_oneof(filters)
    return lookup_all_matching(cls, client, id_rep,
                               lookup_filter=lookup_filter,
                               resources=resources)


def lookup_one_id(cls, client, id_rep, mac=False, resources=None):
    resources = lookup_all_id(cls, client, id_rep,
                              mac=mac,
                              resources=resources)
    resources_len = len(list(resources)) if resources is not None else 0
    if resources_len == 1:
        return resources[0]
    elif resources_len == 0:
        raise KeyError('Id: {} does not exist'.format(id_rep))
    else:
        ambig_ids = [res.id for res in resources]
        ambig_list = '({})'.format(', '.join(ambig_ids))
        raise KeyError('Ambiguous id: {} {}'.format(id_rep, ambig_list))


helium.Resource.lookup_matching = classmethod(lookup_all_matching)
helium.Resource.lookup_all = classmethod(lookup_all_id)
helium.Resource.lookup = classmethod(lookup_one_id)
helium.Resource.short_id = property(lambda self: self.id.split('-')[0])

Resource = helium.Resource
ResourceMeta = helium.ResourceMeta
