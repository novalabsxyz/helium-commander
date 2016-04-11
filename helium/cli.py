import commands
import helium
import click

@click.command(cls=commands.Loader)
@click.option('--api-key',
              envvar='HELIUM_API_KEY',
              required=True,
              help='your Helium API key. Can also be specified using the HELIUM_API_KEY environment variable')
@click.option('--host',
              envvar='HELIUM_API_URL',
              default=None,
              help= 'The Helium base API URL. Can also be specified using the HELIUM_API_URL environment variable.' )
@click.pass_context
def cli(ctx, api_key, host):
    ctx.obj = helium.Service(api_key, host)


def main():
    import sys
    args = sys.argv[1:]
    cli.main(args=args, prog_name=None)

if __name__ == '__main__':
    main()
