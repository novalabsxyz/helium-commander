import dpath.util as dpath
import urlparse
import requests
import click
import helium
import util

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on cloud-scripts
    """
    pass

def _tabulate(result):
    def _map_script_filenames(json):
        files = dpath.get(json, 'meta/scripts')
        return ','.join(_extract_script_filenames(files))

    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('state', 'attributes/state'),
        ('name', 'attributes/name'),
        ('files', _map_script_filenames)
    ]))


def _extract_script_filenames(files):
    return [urlparse.urlsplit(url).path.split('/')[-1] for url in files]


@cli.command()
@pass_service
def list(service):
    """List all known cloud-scripts.

    Lists all cloud-scripts for the organization.
    """
    _tabulate(service.get_cloud_scripts().get('data'))

@cli.command()
@click.argument('script')
@pass_service
def start(service, script):
    """Starts a given cloud-script.

    Starts the SCRIPT with the given id.
    """
    _tabluate([service.update_cloud_script(script, start=True).get('data')])

@cli.command()
@click.argument('script')
@pass_service
def stop(service, script):
    """Stop a given cloud-script.

    Stops the SCRIPT with the given id.
    """
    _tabluate([service.update_cloud_script(script, start=False).get('data')])


@cli.command()
@click.argument('script')
@click.argument('file')
@pass_service
def show(service, script, file):
    """Gets a script file from a given cloud-script.

    Fetches a FILE from a given cloud-SCRIPT.
    """
    json = service.get_cloud_script(script).get('data')
    file_urls = [f.encode('utf-8') for f in dpath.get(json, 'meta/scripts')]
    names = dict(zip(_extract_script_filenames(file_urls), file_urls))
    file_url = names[opts.file]
    click.echo(requests.get(file_url).text())
