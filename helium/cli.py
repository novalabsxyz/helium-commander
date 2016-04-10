import commands
import helium
import click

@click.command(cls=commands.Loader)
@click.option('-k', '--api-key',
              envvar='HELIUM_API_KEY',
              required=True,
              help='your Helium API key. Can also be specified using the HELIUM_API_KEY environment variable')
@click.pass_context
def cli(ctx, api_key):
    ctx.obj = helium.Service(api_key)


def main():
    import sys
    args = sys.argv[1:]
    cli.main(args=args, prog_name=None)

if __name__ == '__main__':
    main()
