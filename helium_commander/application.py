import argparse
import commands
import json
import helium

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--api-key', required=True,
                        action=commands.EnvDefault, envvar="HELIUM_API_KEY",
                        help='your Helium API key. Can also be specified using the HELIUM_API_KEY environment variable ')

    commands.register_commands(parser)
    opts = parser.parse_args()
    service = helium.Service(opts.api_key)

    # execute the command
    result = commands.perform_command(service, opts)
    if result:
        print result
