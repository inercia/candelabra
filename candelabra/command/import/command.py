#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.base import Command
from candelabra.boxes import boxes_storage_factory
from candelabra.errors import ImportException


logger = getLogger(__name__)


class ImportCommand(Command):
    NAME = 'import'
    DESCRIPTION = "import a box from a file/URL."

    def argparser(self, parser):
        """ Parse arguments
        """
        parser.add_argument('--input-format',
                            type=basestring,
                            dest='box_format',
                            default=None,
                            help='input format for the image')
        parser.add_argument('-n',
                            '--name',
                            dest='box_name',
                            default=None,
                            type=str,
                            help='the box name')
        parser.add_argument('--url',
                            dest='box_url',
                            default=None,
                            type=str,
                            help='a URL where the input image/box is imported from')

    def run(self, args, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

        boxes_storage = boxes_storage_factory()
        if args.box_name is None:
            raise ImportException('no name provided for the box')
        if boxes_storage.has_box(args.box_name):
            raise ImportException('there is already a box called "%s"', args.box_name)
        if args.box_url is None:
            raise ImportException('no URL provided for importing the box "%s"', args.box_name)

        box = boxes_storage.get_box(name=args.box_name, url=args.box_url)
        box.do_download()


command = ImportCommand()
