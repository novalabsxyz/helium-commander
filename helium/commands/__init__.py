from importlib import import_module
import click

__commands__ = [
    "label",
    "sensor",
    "element",
    "sensor-script",
    "cloud-script",
    "organization",
    "user"
]


class Loader(click.MultiCommand):
    def list_commands(self, ctx):
        __commands__.sort()
        return __commands__
    def get_command(self, ctx, name):
        try:
            command = import_module(__name__+"."+name)
        except ImportError, e:
            print e
            return
        return command.cli
