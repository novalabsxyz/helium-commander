About
=====

Helium_ is an integrated platform of smart sensors, communication, edge
and cloud compute that enables numerous sensing applications.

This package makes it easy to talk to the Helium API_. It offers:

* A command line interface to interact with the various Helium
  endpoints
* A service API that shows how to communicate with the Helium API and
  interpret the results.

Installation
============


Source
------

Use this if you're actively developing or extending

::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -e .


PyPi
----

From PyPi_. Use this if you want to use the
command line tool on its own.

::

    $ pip install helium-commander

Note that on some systems you may have to use `sudo` to install the
package system-wide

::

   $ sudo pip install helium-commander


Nix
---

helium-commander can also be installed using the Nix_ package manager. Clone
the repository and run:

::

   $ nix-env --install --file default.nix

To upgrade on version releases, run:

::

   $ nix-env --upgrade --file default.nix


Usage
=====

To use the `helium` command, explore the help options:

::

    $ helium --help
    Usage: helium [OPTIONS] COMMAND [ARGS]...

    Options:
      -k, --api-key TEXT  your Helium API key. Can also be specified using the
                          HELIUM_API_KEY environment variable  [required]
      --help              Show this message and exit.

    Commands:
      cloud-script   Operations on cloud-scripts
      element        Operations on elements.
      label          Operations on labels of sensors.
      organization   Operations on physical or virtual sensors.
      sensor         Operations on physical or virtual sensors.
      sensor-script  Operations on sensor-script.


.. _Helium: https://helium.com
.. _API: https://docs.helium.com
.. _PyPi: https://pypi.python.org
.. _Nix: https://nixos.org/nix/
