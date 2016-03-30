import dpath.util as dpath
import sensor

def list(service ,opts):
    if not opts.labels:
        return service.get_labels().get('data')
    else:
        return [service.get_label(id).get('data') for id in opts.labels]

def create(service, opts):
    label = service.create_label(opts.name).get('data')
    if opts.sensors:
        service.update_label_sensors(label['id'], opts.sensors)
    return [label]

def delete(service, opts):
    result = service.delete_label(opts.label)
    return "Deleted" if result.status_code == 204 else result

def add(service, opts):
    sensors = service.get_label_sensors(opts.label).get('data')
    sensor_ids = dpath.values(sensors, "*/id")
    sensor_ids = set(sensor_ids).union(set(opts.sensor))
    service.update_label_sensors(opts.label, sensor_ids)
    return sensor.list(service, opts)

def remove(service, opts):
    sensors = service.get_label_sensors(opts.label).get('data')
    sensor_ids = dpath.values(sensors, "*/id")
    sensor_ids = set(sensor_ids).difference(set(opts.sensor))
    if sensor_ids is None: sensor_ids = []
    service.update_label_sensors(opts.label, sensor_ids)
    return sensor.list(service, opts)

def _register_commands(parser):
    name_mapping={
        'id': 'id',
        'name': 'attributes/name'
    }
    #list
    list_parser = parser.add_parser("list", help="list all or specific labels")
    list_parser.set_defaults(command=list, mapping=name_mapping)
    list_parser.add_argument("labels", metavar="LABEL", nargs="*",
                             help="the id of a label")

    #create
    create_parser = parser.add_parser("create", help="create a label")
    create_parser.set_defaults(command=create, mapping=name_mapping)
    create_parser.add_argument("-n", "--name", required=True,
                               help="the name for the new label")
    create_parser.add_argument("sensors", metavar="SENSOR", nargs="*",
                               help="the sensor id to add to the label")

    #delete
    delete_parser = parser.add_parser("delete", help="delete a label")
    delete_parser.set_defaults(command=delete)
    delete_parser.add_argument("label", help="the id of the label to delete")

    # add
    add_parser = parser.add_parser("add", help="add sensors to a label")
    add_parser.set_defaults(command=add, mapping=name_mapping)
    add_parser.add_argument("label", help="the id of the label to add to")
    add_parser.add_argument("-s", "--sensor", nargs="+",
                            help="the sensor ids to add")

    # remove
    remove_parser = parser.add_parser("remove", help="remove sensors from a label")
    remove_parser.set_defaults(command=remove, mapping=name_mapping)
    remove_parser.add_argument("label", help="the id of the label to remove from")
    remove_parser.add_argument("-s", "--sensor", nargs="+",
                               help="the sensor ids to remove")
