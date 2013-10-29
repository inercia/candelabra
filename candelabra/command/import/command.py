#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
import os
import tempfile

from candelabra.base import Command
from candelabra.errors import ImportException
from candelabra.scheduler.base import Scheduler


logger = getLogger(__name__)


#: a mbyte
MBYTE = 1024 * 1024


class ImportCommand(Command):
    DESCRIPTION = "import a box from a file/URL."

    def argparser(self, parser):
        """ Parse arguments
        """
        parser.add_argument('--input-format',
                            type=basestring,
                            dest='format',
                            help='input format for the image')
        parser.add_argument('--url',
                            dest='url',
                            type=str,
                            help='a URL where the input image/box is imported from')

    def run(self, args, topology, command):
        """ Run the command
        """
        logger.info('running command "%s"', command)

        self.args = args

        scheduler = Scheduler()

        logger.info('adding tasks...')
        scheduler.append([
            (self.do_download_image, ),
            (self.do_add_to_storage, self.do_download_image),
        ])
        scheduler.run(abort_on_error=True)

    #####################
    # tasks
    #####################

    def do_download_image(self):
        """ Download the image
        """
        if self.args.url is None:
            raise ImportException('input URL not specified')
        else:
            import pycurl

            logger.info('downloading image from "%s"', self.args.url)

            curl = pycurl.Curl()
            fp, name = tempfile.mkstemp()
            try:
                f = os.fdopen(fp, 'w+')
                logger.info('... downloading to temporal file "%s"', name)

                self.downloaded_mbytes = 0

                def cb_progress(download_t, download_d, upload_t, upload_d):
                    dmbytes = int(download_d / MBYTE)
                    if dmbytes > self.downloaded_mbytes:
                        logger.debug('downloaded=%d Mb, total=%d Mbytes', dmbytes, download_t / MBYTE)
                        self.downloaded_mbytes = dmbytes

                curl.setopt(pycurl.URL, str(self.args.url))
                curl.setopt(pycurl.WRITEFUNCTION, f.write)
                curl.setopt(curl.NOPROGRESS, 0)
                curl.setopt(curl.PROGRESSFUNCTION, cb_progress)
                curl.perform()
            except KeyboardInterrupt:
                logger.debug('... removing %s', name)
                os.remove(name)
                raise ImportException('could not perform download')
            except Exception, e:
                logger.critical('while downloading: %s', str(e))
                logger.debug('... removing %s', name)
                os.remove(name)
                raise ImportException('could not perform download')
            else:
                logger.info('downloaded %d bytes!', self.downloaded_mbytes)
            finally:
                curl.close()
                fp.close()

    def do_add_to_storage(self):
        """ Add the image to the storage
        """
        logger.debug('adding image to storage')

        # prepare the storage directory

        # move the file

        # detect the format

        # uncompress it (if we need it)

        # save the format, details, etc...


command = ImportCommand()
