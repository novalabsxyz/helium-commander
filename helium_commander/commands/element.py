def list(service ,opts):
    if not opts.elements:
        return service.get_elements().get('data')
    else:
        return [service.get_element(id).get('data') for id in opts.elements]

def _register_commands(parser, action):
    list_parser = parser.add_parser("list", help="list all or specific elements")
    list_parser.add_argument("elements", metavar="ELEMENT", nargs="*",
                             action=action(list, {
                                 'id': 'id',
                                 'name': 'attributes/name'
                             }),
                             help="the id of an element")
