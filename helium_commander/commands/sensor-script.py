import dpath.util as dpath

def list(service, opts):
    return service.get_sensor_scripts().get('data')

def _map_progress(json):
    progress = dpath.values(json, "relationships/status/data/*/meta/progress")
    return sum(progress)/len(progress) if len(progress) > 0 else 0

def _map_sensor_count(json):
    targets = dpath.get(json, "relationships/status/data")
    return len(targets)

def status(service, opts):
    script_info = service.get_sensor_script(opts.script)
    return dpath.get(script_info, 'data/relationships/status/data')

def deploy(service, opts):
    return [service.deploy_sensor_script(opts.files,
                                        labels=opts.labels,
                                        sensors=opts.sensors).get('data')]

def _register_commands(parser):
    # list
    list_mapping= [
        ('id', 'id'),
        ('created', 'meta/created'),
        ('sensors', _map_sensor_count),
        ('progress', _map_progress)
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

    # deploy
    deploy_parser = parser.add_parser("deploy", help="deploy a script to sensors or a label")
    deploy_parser.set_defaults(command=deploy, mapping=list_mapping)
    deploy_parser.add_argument('-f', '--files', metavar="FILE", nargs='+',
                               help='a script filename')
    deploy_parser.add_argument('-s', '--sensors', metavar="SENSOR", nargs='+',
                               help='the id for a sensor')
    deploy_parser.add_argument('-l', '--labels', metavar="LABEL", nargs='+',
                               help='the id for a label')
