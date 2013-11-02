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


Example topology
================

Manchines topologies are defined in topology files like this:

	candelabra:

	  default:

	    box:
	      name:       centos64
	      url:        http://shonky.info/centos64.box

	    provisioner:
	      class: puppet

	    shared:
	      - local:    docs
	        remote:   /home/docs
	      - local:    $HOME
	        remote:   /home/host_home

	  networks:
	    - class:  private
	      name:   private

	  machines:

	    - machine:
	        class:    virtualbox
	        name:     vm1
	        hostname: vm1
	        network:
	          class:  automatic

	    - machine:
	        class:    virtualbox
	        name:     vm2
	        hostname: vm2
	        network:
	          class:  automatic

In this topology, two machines will be setup, with two shared folders and automatic networking.

Development
===========

You can run the unit test with (needs `nose`):

	$ make test

If you have the `coverage` program installed, you can generate coverage reports with:

    $ make coverage


    