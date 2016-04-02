def list(service ,opts):
    if not opts.elements:
        return service.get_elements().get('data')
    else:
        return [service.get_element(id).get('data') for id in opts.elements]

def _register_commands(parser):
    list_mapping=[
        ('id', 'id'),
        ('mac', 'meta/mac'),
        ('name', 'attributes/name')
    ]
    list_parser = parser.add_parser("list", help="list all or specific elements")
    list_parser.set_defaults(command=list, mapping=list_mapping)
    list_parser.add_argument("elements", metavar="ELEMENT", nargs="*",
                             help="the id of an element")
