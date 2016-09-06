from __future__ import unicode_literals

import helium


class Client(helium.Client):

    def __init__(self, **kwargs):
        token = kwargs.pop("api_token", None)
        url = kwargs.pop('base_url', None)
        super(Client, self).__init__(api_token=token, base_url=url)

        self.uuid = kwargs.pop('uuid', False)
        self.format = kwargs.pop('format', 'tabular')
