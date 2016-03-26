def list(service ,opts):
    if not opts.labels:
        return service.get_labels().get('data')
    else:
        return [service.get_label(id).get('data') for id in opts.labels]

def _register_commands(parser, action):
    list_parser = parser.add_parser("list", help="list all or specific labels")
    list_parser.add_argument("labels", metavar="LABEL", nargs="*",
                             action=action(list, {
                                 'id': 'id',
                                 'name': 'attributes/name'
                             }),
                             help="the id of a label")
