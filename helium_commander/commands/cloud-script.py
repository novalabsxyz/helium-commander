import dpath.util as dpath

def list(service, opts):
    return service.get_cloud_scripts().get('data')

def start(service, opts):
    return [service.update_cloud_script(opts.script, start=True).get('data')]

def stop(service, opts):
    return [service.update_cloud_script(opts.script, start=False).get('data')]

def create(service, opts):
    return

def _register_commands(parser):
    # list
    list_mapping= [
        ('id', 'id'),
        ('state', 'attributes/state'),
        ('name', 'attributes/name'),
    ]
    list_parser = parser.add_parser("list", help="list all or a specific cloud-script")
    list_parser.set_defaults(command=list, mapping=list_mapping)

    # start
    start_parser = parser.add_parser("start", help="start the given cloud-script")
    start_parser.set_defaults(command=start, mapping=list_mapping)
    start_parser.add_argument("script", metavar="SCRIPT",
                               help="the id of a script to list")

    # start
    start_parser = parser.add_parser("start", help="start the given cloud-script")
    start_parser.set_defaults(command=start, mapping=list_mapping)
    start_parser.add_argument("script", metavar="SCRIPT",
                              help="the id of a script to start")

    # stop
    stop_parser = parser.add_parser("stop", help="stop the given cloud-script")
    stop_parser.set_defaults(command=stop, mapping=list_mapping)
    stop_parser.add_argument("script", metavar="SCRIPT",
                               help="the id of a script to stop")
