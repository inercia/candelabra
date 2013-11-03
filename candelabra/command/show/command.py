#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.plugins import CommandPlugin
from candelabra.errors import UnsupportedCommandException

logger = getLogger(__name__)


class ShowCommandPlugin(CommandPlugin):
    NAME = 'show'
    DESCRIPTION = "show information."

    def argparser(self, parser):
        """ Parse arguments
        """
        subparsers = parser.add_subparsers(help='sub-commands available for showing',
                                           dest='show_command')

        # boxes
        parser_boxes = subparsers.add_parser('boxes',
                                             help='show the list of boxes')
        parser_boxes.add_argument('-v',
                                  '--verbose',
                                  action='store_true',
                                  help='verbose display')

        # topologies
        parser_topo = subparsers.add_parser('topologies',
                                            help='show the list of created topologies')
        parser_topo.add_argument('-v',
                                 '--verbose',
                                 action='store_true',
                                 help='verbose display')

        # status
        parser_status = subparsers.add_parser('status',
                                              help='show the machines statuses')
        parser_status.add_argument('-t',
                                   '--topology',
                                   metavar='TOPOLOGY',
                                   dest='topology',
                                   type=str,
                                   default=None,
                                   help='the machine(s) definition(s) file(s)')
        parser_status.add_argument('-v',
                                   '--verbose',
                                   action='store_true',
                                   help='verbose display')

    def run(self, args, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

        if args.show_command == 'boxes':
            self.do_show_boxes(args)
        elif args.show_command == 'status':
            self.do_show_status(args)
        else:
            raise UnsupportedCommandException('unknown subcommand "%s"' % args.show_command)

    #####################
    # tasks
    #####################

    def do_show_status(self, args):
        """ Show the status of the machines in the topology
        """
        topology = self.run_with_topology(args, args.topology, save_state=False)
        for machine in topology.machines:
            if not machine.is_global:
                logger.info('machine: %s', machine.cfg_name)
                logger.info('... state: %d [%s]', int(machine.state), machine.state_str)

    def do_show_boxes(self, args):
        """ Show all the boxes in the system
        """
        from candelabra.boxes import boxes_storage_factory

        boxes_storage = boxes_storage_factory()
        for box_name, box in boxes_storage.boxes.iteritems():
            logger.info('box info:')
            logger.info('%s = %s', box_name, box)


command = ShowCommandPlugin()

