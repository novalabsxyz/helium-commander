import click
from functools import reduce
from json import loads as load_json


def sort_option(choices):
    options = [
        click.option('--reverse', is_flag=True,
                     help='Sort in reverse order'),
        click.option('--sort', type=click.Choice(choices),
                     help='How to sort the result')
    ]

    def wrapper(func):
        for option in reversed(options):
            func = option(func)
        return func
    return wrapper


def device_sort_option(f):
    return sort_option(['seen', 'name', 'created'])(f)


def device_mac_option(f):
    return click.option('--mac', is_flag=True,
                        help="Whether the given id(s) are a mac address")(f)


def metadata_filter_option(f):
    return click.option('--metadata', metavar='FILTER',
                        type=JSONParamType(),
                        help="A metadata filter to use")(f)


class ResourceParamType(click.ParamType):
    name = 'resource'

    def __init__(self, metavar='TEXT'):
        self.metavar = metavar

    def get_metavar(self, param):
        return '{0}[,{0},...]* | @filename'.format(self.metavar)

    def convert(self, value, param, ctx):
        def collect_resources(acc, resource_rep):
            if resource_rep.startswith('@'):
                for line in click.open_file(resource_rep[1:]):
                    acc.append(line.strip())
            else:
                acc.append(resource_rep)
            return acc
        value = value.split(',')
        return reduce(collect_resources, value, [])

    def __repr__(self):
        'Resource(metavar={})'.fomat(self.metavar)


class JSONParamType(click.ParamType):
    name = 'JSON'

    def convert(self, value, param, ctx):
        try:
            return load_json(value)
        except ValueError:
            self.fail('{} is not a valid json value'.format(value), param, ctx)
