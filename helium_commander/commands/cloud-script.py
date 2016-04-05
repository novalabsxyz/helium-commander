import dpath.util as dpath
import urlparse
import requests

def _extract_script_filenames(files):
    return [urlparse.urlsplit(url).path.split('/')[-1] for url in files]

def _map_script_filenames(json):
    files = dpath.get(json, 'meta/scripts')
    return ','.join(_extract_script_filenames(files))

def list(service, opts):
    return service.get_cloud_scripts().get('data')

def start(service, opts):
    return [service.update_cloud_script(opts.script, start=True).get('data')]

def stop(service, opts):
    return [service.update_cloud_script(opts.script, start=False).get('data')]

def show(service, opts):
    json = service.get_cloud_script(opts.script).get('data')
    file_urls = [f.encode('utf-8') for f in dpath.get(json, 'meta/scripts')]
    names = dict(zip(_extract_script_filenames(file_urls), file_urls))
    file_url = names[opts.file]
    return requests.get(file_url).text()


def create(service, opts):
    return

def _register_commands(parser):
    # list
    list_mapping= [
        ('id', 'id'),
        ('state', 'attributes/state'),
        ('name', 'attributes/name'),
        ('files', _map_script_filenames)
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

    # show
    show_parser = parser.add_parser("show", help="stop a given file from a cloud-script")
    show_parser.set_defaults(command=show)
    show_parser.add_argument("script", metavar="SCRIPT",
                               help="the id of a script to get the file from")
    show_parser.add_argument("file", metavar="FILENAME",
                             help="the name of the file to get")
