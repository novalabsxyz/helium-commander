import dpath.util as dpath

def list(service, opts):

    if opts.label:
        labels = service.get_label(opts.label).get('data')
        # TODO: Use include query param once available to avoid N+1 queries
        label_sensors = dpath.values(labels, "relationships/sensor/data/*/id")
        return [service.get_sensor(id).get('data') for id in label_sensors]
    elif opts.sensors:
        return [service.get_sensor(id).get('data') for id in opts.sensors]
    else:
        return service.get_sensors().get('data')

def create(service, opts):
    return


def _register_commands(parser):
    list_parser = parser.add_parser("list", help="list all or specific sensors")
    list_parser.set_defaults(command=list,
                             mapping= {
                                 'id': 'id',
                                 'name': 'attributes/name'
                             })
    list_source_group=list_parser.add_mutually_exclusive_group()
    list_source_group.add_argument("-s", "--sensors", metavar="SENSOR", nargs="*",
                                   help="the id of a sensor")
    list_source_group.add_argument("-l", "--label",
                                   help='the id for a label')
