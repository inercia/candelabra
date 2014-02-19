Overview
========

*Candelabra* is a virtual machines manager, similar to Vagrant but more focused on the having multiple machines running at the same time.

[![Build Status](https://drone.io/github.com/inercia/candelabra/status.png)](https://drone.io/github.com/inercia/candelabra/latest)

Status
======

Candelabra's current status is probably something between ALPHA and BETA. SO do not use
it yet for anything serious...

Documentation
=============

See the onine docs at:

http://inercia.github.io/candelabra

Running
=======

You can install it from the source code with

	$ pip install git+https://github.com/inercia/candelabra

The you can run `candelabra` with

	$ candelabra --help

See the topology examples, like `machines.yaml`.


Topologies
==========

Manchines topologies are defined in _topology files_: YAML files where we can define how the topology is built. For example:

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

In this topology, two VirtualBox machines will be started, with two shared folders, automatic networking and provisioned with Puppet.

Development
===========

You can run the unit test with (needs `nose`):

	$ make test

If you have the `coverage` program installed, you can generate coverage reports with:

    $ make coverage


