import click


def sort_option(choices):
    options = [
        click.option('--reverse', is_flag=True,
                     help='Sort in reverse order'),
        click.option('--sort', type=click.Choice(choices),
                     help='How to sort the result')
    ]

    def wrapper(func):
        for option in reversed(options):
            func = option(func)
        return func
    return wrapper


def device_sort_option(f):
    return sort_option(['seen', 'name'])(f)


def device_mac_option(f):
    return click.option('--mac', is_flag=True,
                        help="Whether the given id is a mac address")(f)
