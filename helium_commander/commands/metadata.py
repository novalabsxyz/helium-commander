"""Metadata cli generator."""
import click

from helium_commander import Client, Metadata
from helium_commander import JSONParamType

pass_client = click.make_pass_decorator(Client)


def cli(cls, singleton=False):
    group = click.Group(name='metadata',
                        short_help="Commands on metadata.")
    resource_type = cls._resource_type()

    def _fetch_resource(client, id, **kwargs):
        if singleton:
            resource = cls.singleton(client)
        else:
            mac = kwargs.pop('mac', None)
            resource = cls.lookup(client, id, mac=mac)
        return resource

    def _id_argument():
        def wrapper(func):
            if not singleton:
                return click.argument('id', metavar=resource_type)(func)
            return func
        return wrapper

    @group.command('list')
    @_id_argument()
    @pass_client
    def _list(client, id=None, **kwargs):
        """Get metadata."""
        resource = _fetch_resource(client, id, **kwargs)
        metadata = resource.metadata()
        Metadata.display(client, [metadata], **kwargs)

    @group.command('update')
    @_id_argument()
    @click.argument('value', type=JSONParamType())
    @pass_client
    def _update(client, value, id=None, **kwargs):
        """Update metadata."""
        resource = _fetch_resource(client, id, **kwargs)
        metadata = resource.metadata()
        if value is not None:
            metadata = metadata.update(value)
        Metadata.display(client, [metadata], **kwargs)

    @group.command('replace')
    @_id_argument()
    @click.argument('value', type=JSONParamType())
    @pass_client
    def _replace(client, value, id=None, **kwargs):
        """Replace metadata."""
        resource = _fetch_resource(client, id, **kwargs)
        metadata = resource.metadata()
        if value is not None:
            metadata = metadata.replace(value)
        Metadata.display(client, [metadata], **kwargs)

    return group
