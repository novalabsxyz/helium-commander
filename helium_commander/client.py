from __future__ import unicode_literals

import click
import helium
import helium_commander.writer as writer


class Client(helium.Client):

    def __init__(self, **kwargs):
        token = kwargs.pop("api_token", None)
        url = kwargs.pop('base_url', None)
        super(Client, self).__init__(api_token=token, base_url=url)

        file = kwargs.pop('file', click.utils.get_text_stream('stdout'))
        format = kwargs.pop('format', 'tabular')
        format = writer.output_format(**kwargs)
        self.writer = writer.for_format(format, file, **kwargs)
