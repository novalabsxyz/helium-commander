import dpath.util as dpath
import requests
import click
import helium
import util
import timeseries as ts

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on cloud-scripts.
    """
    pass

def _tabulate(result):
    util.tabulate(result, [
        ('id', util.shorten_json_id),
        ('state', 'attributes/state'),
        ('name', 'attributes/name'),
        ('files', util.map_script_filenames),
        ('error', 'attributes/error/error')
    ])


@cli.command()
@pass_service
def list(service):
    """List all known cloud-scripts.

    Lists all cloud-scripts for the organization.
    """
    _tabulate(service.get_cloud_scripts().get('data'))

@cli.command()
@click.argument('script')
@click.option('--name',
              help="the new name for the script")
@pass_service
def start(service, script, **kwargs):
    """Starts a given cloud-script.

    Starts the SCRIPT with the given id.
    """
    script = util.lookup_resource_id(service.get_cloud_scripts, script)
    _tabulate([service.update_cloud_script(script, state="running", **kwargs).get('data')])

@cli.command()
@click.argument('script')
@click.option('--name',
              help="the new name for the script")
@pass_service
def stop(service, script, **kwargs):
    """Stop a given cloud-script.

    Stops the SCRIPT with the given id.
    """
    script = util.lookup_resource_id(service.get_cloud_scripts, script)
    _tabulate([service.update_cloud_script(script, state="stopped", **kwargs).get('data')])


@cli.command()
@click.argument('script')
@pass_service
def delete(service, script):
    """Delete a given cloud-script.

    Deletes the cloud-SCRIPT with the given id.
    """
    script = util.lookup_resource_id(service.get_cloud_scripts, script)
    result = service.delete_cloud_script(script)
    click.echo("Deleted: " + script.encode('ascii')
               if result.status_code == 204 else result)


@cli.command()
@click.argument('script')
@ts.options()
@pass_service
def timeseries(service, script, **kwargs):
    """List readings for a cloud-script.

    Lists one page of readings for a given SCRIPT.
    """
    script = util.lookup_resource_id(service.get_cloud_scripts, script)
    data = service.get_cloud_script_timeseries(script, **kwargs).get('data')
    ts.tabulate(data, **kwargs)


@cli.command()
@click.argument('script')
@click.argument('file')
@pass_service
def show(service, script, file):
    """Gets a script file from a given cloud-script.

    Fetches a FILE from a given cloud-SCRIPT.
    """
    script = util.lookup_resource_id(service.get_cloud_scripts, script)
    json = service.get_cloud_script(script).get('data')
    file_urls = [f.encode('utf-8') for f in dpath.get(json, 'meta/scripts')]
    names = dict(zip(util.extract_script_filenames(file_urls), file_urls))
    file_url = names[file]
    click.echo(requests.get(file_url).text)


@cli.command()
@click.argument('file', nargs=-1)
@click.option('--main', type=click.Path(exists=True),
              help="The main file for the script")
@click.option('--name',
              help="the name for the script")
@click.option('--state', type=click.Choice(['running', 'stopped']),
              default='running',
              help="the starting state for the script (default 'running')")
@pass_service
def deploy(service, file, **kwargs):
    """Deploy  a cloud-script.

    Submits a deploy request of one ore more FILEs.
    Optionally specify a name and the starting state of the script once
    it is deployed.

    If the --main option is specified the given file is used as the `user.lua`,
    i.e. the main user script for the deployment. The file may  be part of
    the list of files given to make it easier to specify wildcards.

    Note: One of the given files _must_ be called user.lua if the --main option is not given.
    This file will be considered the primary script for the deploy.
    """
    deploy=service.deploy_cloud_script(file, **kwargs).get('data')
    _tabulate([deploy])


@cli.command()
@click.argument('script')
@pass_service
def status(service, script):
    """Displays current status information for a script.

    Display status information a given SCRIPT. If the script is in an error
    condition the error details are displayed.
    """
    script = util.lookup_resource_id(service.get_cloud_scripts, script)
    data = service.get_cloud_script(script).get('data')
    click.echo('Status: ' + dpath.get(data, "attributes/state"))
    try:
        error = dpath.get(data, "attributes/error")
    except KeyError:
        error = None
    # Pull out the details if they're there
    if isinstance(error, dict):
        error = error.get('details')
    if error:
        click.echo('Error: ' + error)
