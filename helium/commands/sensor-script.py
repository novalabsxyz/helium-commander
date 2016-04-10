import click
import util
import helium
import dpath.util as dpath

pass_service=click.make_pass_decorator(helium.Service)

@click.group()
def cli():
    """Operations on sensor-script.
    """
    pass

def _tabulate_scripts(result):
    def _map_sensor_count(json):
        targets = dpath.get(json, "relationships/status/data")
        return len(targets)

    def _map_progress(json):
        progress = dpath.values(json, "relationships/status/data/*/meta/progress")
        return sum(progress)/len(progress) if len(progress) > 0 else 0

    util.output(util.tabulate(result, [
        ('id', 'id'),
        ('created', 'meta/created'),
        ('sensors', _map_sensor_count),
        ('progress', _map_progress)
    ]))

def _tabulate_status(result):
    util.output(util.tabulate(result, [
        ('sensor', 'id'),
        ('mac', 'meta/mac'),
        ('progress', 'meta/progress')
    ]))


@cli.command()
@pass_service
def list(service):
    """List all known sensor-scripts.
    """
    _tabulate_scripts(service.get_sensor_scripts().get('data'))


@cli.command()
@click.argument('script')
@pass_service
def status(service, script):
    """Get status for a script.

    Retrieves the current status for a sensor-script deploy request.
    """
    script_info = service.get_sensor_script(script)
    _tabulate_status(dpath.get(script_info, 'data/relationships/status/data'))


@cli.command()
@click.argument('file', nargs=-1)
@click.option('-l', '--label', multiple=True,
              help="the id of a label")
@click.option('-s', '--sensor', multiple=True,
              help="the id of a sensor")
@pass_service
def deploy(service, file, label, sensor):
    """Deploy a sensor-script.

    Submit a deploy request of one or more FILEs. The targets for the deploy can
    be given as a combination of specific sensors or labels.

    Note: One of the given files _must_ be called user.lua. This file will be
    considered the primary script file for the deploy.

    """
    deploy=service.deploy_sensor_script(file, labels=label, sensors=sensor).get('data')
    _tabulate_scripts([deploy])
