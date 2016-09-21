# Helium Commander

[![Build Status](https://travis-ci.org/helium/helium-commander.svg?branch=master)](https://travis-ci.org/helium/helium-commander)
[![Build status](https://ci.appveyor.com/api/projects/status/i5bocfry81whgaqx?svg=true)](https://ci.appveyor.com/project/madninja/helium-commander)
[![Coverage Status](https://coveralls.io/repos/github/helium/helium-commander/badge.svg?branch=master)](https://coveralls.io/github/helium/helium-commander?branch=master)
[![Code Climate](https://codeclimate.com/github/helium/helium-commander/badges/gpa.svg)](https://codeclimate.com/github/helium/helium-commander)

[Helium](https://helium.com) is an integrated platform of smart sensors, communication, edge and cloud compute that enables numerous sensing applications.

Helium Commander makes it easy to talk to the [Helium API](https://docs.helium.com). It offers:

* A command line interface to interact with the various Helium endpoints
* A service API that shows how to communicate with the Helium API and interpret the results.

## Installation


### From PyPi

From [PyPi](https://pypi.python.org). Use this if you want to use the command line tool on its own.


```
$ pip install helium-commander
```

Note that on some systems you may have to use `sudo` to install the package system-wide.

```
$ sudo pip install helium-commander
```

To upgrade from a previous version:

```
$ pip install helium-commander --upgrade -I
```

**Note**: Ensure that you use `-I` to allow clean upgrades of packages


### From Source

Use this if you're actively developing or extending Commander:

```
$ virtualenv env
$ source env/bin/activate
$ pip install -e .
```


### Nix

`helium-commander` can also be installed using the [Nix](https://nixos.org/nix/) package manager. Clone the repository and run:


```
$ nix-env --install --file default.nix
```

To upgrade on version releases, run:


```
$ nix-env --upgrade --file default.nix
```

## Usage

To use the `helium` command, explore the `--help` options:

```
$ helium --help
Usage: helium [OPTIONS] COMMAND [ARGS]...

Options:
  --version                     Show the version and exit.
  --format [csv|json|tabular]   The output format (default 'tabular')
  --uuid                        Whether to display long identifiers
  --host TEXT                   The Helium base API URL. Can also be specified
                                using the HELIUM_API_URL environment variable.
  --api-key TEXT                your Helium API key. Can also be specified using
                                the HELIUM_API_KEY environment variable
  -h, --help                    Show this message and exit.

Commands:
  element        Operations on elements.
  label          Operations on labels of sensors.
  organization   Operations on the authorized organization
  sensor         Operations on physical or virtual sensors.
  user           Operations on the user.
```

##  Helium Documentation and Community Support

* **Docs** Complete documenation for all parts of Helium can be found at [docs.helium.com](https://docs.helium.com).

##  Helium Documentation and Community Support


* **Docs** Complete documenation for all parts of Helium can be found at [docs.helium.com](https://docs/helium.com).

* **chat.helium.com** - If you have questions or ideas about how to use this code - or any part of Helium - head over the [chat.helium.com](http://chat.helium.com). We're standing by to help.
