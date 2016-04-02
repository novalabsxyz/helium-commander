import dpath.util as dpath

def list(service, opts):
    return service.get_sensor_scripts().get('data')

def status(service, opts):
    script_info = service.get_sensor_script(opts.script)
    return dpath.get(script_info, 'data/relationships/status/data')

def create(service, opts):
    return


def _register_commands(parser):
    # list
    list_mapping= [
        ('id', 'id')
    ]
    list_parser = parser.add_parser("list", help="list all or a specific sensor-script")
    list_parser.set_defaults(command=list, mapping=list_mapping)

    # status
    status_mapping = [
        ('sensor', 'id'),
        ('mac', 'meta/mac'),
        ('progress', 'meta/progress')
    ]
    status_parser = parser.add_parser("status", help="show status for a specific sensor-script")
    status_parser.set_defaults(command=status, mapping=status_mapping)
    status_parser.add_argument("script", metavar="SCRIPT",
                               help="the id of a script to list")
