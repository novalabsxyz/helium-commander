import tablib

def list(service, opts):
    if not opts.sensors:
        return service.get_sensors().get('data')
    else:
        return [service.get_sensor(id).get('data') for id in opts.sensors]



def _register_commands(parser):
    list_parser = parser.add_parser("list", help="list all or specific sensors")
    list_parser.set_defaults(command=list,
                             mapping= {
                                 'id': 'id',
                                 'name': 'attributes/name'
                             })
    list_parser.add_argument("sensors", metavar="SENSOR", nargs="*",
                             help="the id of a sensor")
