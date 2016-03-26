def list(service ,opts):
    if not opts.labels:
        return service.get_labels().get('data')
    else:
        return [service.get_label(id).get('data') for id in opts.labels]

def _register_commands(parser):
    list_parser = parser.add_parser("list", help="list all or specific labels")
    list_parser.set_defaults(command=list,
                             mapping= {
                                 'id': 'id',
                                 'name': 'attributes/name'
                             })
    list_parser.add_argument("labels", metavar="LABEL", nargs="*",
                             help="the id of a label")
