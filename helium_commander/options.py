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
    return sort_option(['seen', 'name'])(f)


def device_mac_option(f):
    return click.option('--mac', is_flag=True,
                        help="Whether the given id is a mac address")(f)


class ResourceParamType(click.ParamType):
    name = 'resource'

    def __init__(self, nargs=-1, metavar='TEXT'):
        self.nargs = nargs
        self.metavar = metavar

    def get_metavar(self, param):
        metavar = self.metavar
        if self.nargs == -1:
            return '{0}[,{0},...]* | @filename'.format(metavar)
        else:
            return metavar

    def convert(self, value, param, ctx):
        def collect_resources(acc, resource_rep):
            if resource_rep.startswith('@'):
                for line in click.open_file(resource_rep[1:]):
                    acc.append(line.strip())
            else:
                acc.append(resource_rep)
            return acc
        nargs = self.nargs
        value = value.split(',')
        resources = reduce(collect_resources, value, [])
        if nargs > 0 and nargs != len(resources):
            self.fail('Expected {} resources, but got {}'.format(nargs, len(resources)))
        return resources

    def __repr__(self):
        'Resource(metavar={}, nargs={})'.fomat(self.metavar, self.nargs)


class JSONParamType(click.ParamType):
    name = 'JSON'

    def convert(self, value, param, ctx):
        try:
            return load_json(value)
        except ValueError:
            self.fail('{} is not a valid json value'.format(value), param, ctx)
