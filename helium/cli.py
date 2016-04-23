import commands
import helium
import click

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)

@click.command(cls=commands.Loader, context_settings=CONTEXT_SETTINGS)
@click.option('--api-key',
              envvar='HELIUM_API_KEY',
              help='your Helium API key. Can also be specified using the HELIUM_API_KEY environment variable')
@click.option('--host',
              envvar='HELIUM_API_URL',
              default=None,
              help= 'The Helium base API URL. Can also be specified using the HELIUM_API_URL environment variable.' )
@click.option('--uuid', is_flag=True,
              help="Whether to display long identifiers")
@click.option('--format', type=click.Choice(['csv', 'json', 'tty']), default=None,
              help="The output format (default 'tty')")
@click.pass_context
def cli(ctx, api_key, host, **kwargs):
    ctx.obj = helium.Service(api_key, host)


def main():
    import sys
    args = sys.argv[1:]
    cli.main(args=args, prog_name=None)

if __name__ == '__main__':
    main()
