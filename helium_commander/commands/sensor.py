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
    return [service.create_sensor(opts.name).get('data')]

def delete(service, opts):
    result = service.delete_sensor(opts.sensor)
    return "Deleted" if result.status_code == 204 else result

def _register_commands(parser):
    sensor_mapping=[
        ('id', 'id'),
        ('mac', 'meta/mac'),
        ('name', 'attributes/name'),
    ]
    # list
    list_parser = parser.add_parser("list", help="list all or specific sensors")
    list_parser.set_defaults(command=list, mapping=sensor_mapping)
    list_source_group=list_parser.add_mutually_exclusive_group()
    list_source_group.add_argument("-s", "--sensors", metavar="SENSOR", nargs="*",
                                   help="the id of a sensor")
    list_source_group.add_argument("-l", "--label",
                                   help='the id for a label')

    #create
    create_parser = parser.add_parser("create", help="create a virtual sensor")
    create_parser.set_defaults(command=create, mapping=sensor_mapping)
    create_parser.add_argument("-n", "--name", required=True,
                               help="the name for the new virtual sensor")

    #delete
    delete_parser = parser.add_parser("delete", help="delete a sensor")
    delete_parser.set_defaults(command=delete)
    delete_parser.add_argument("sensor", help="the id of the sensor to delete")
