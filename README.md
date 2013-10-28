Overview
========

*Candelabra* is a virtual machines manager, similar to Vagrant but more focused on the having multiple machines running at the same time.

Running
=======

You can install it from the source code with

	$ pip install git+https://github.com/inercia/candelabra

The you can run `candelabra` with

	$ candelabra --help

See the topology examples, like `machines.yaml`.

Development
===========

You can run the unit test with (needs `nose`):

	$ make test

If you have the `coverage` program installed, you can generate coverage reports with:

    $ make coverage