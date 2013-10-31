#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from candelabra.errors import SchedulerTaskException

from candelabra.scheduler.topsort import topsort

logger = getLogger(__name__)


class Scheduler(object):
    """ A scheduler for tasks
    """

    def __init__(self):
        """ Initialize a scheduler
        """
        self._performed_tasks = set()
        self._target_tasks = []
        self._running = False

    def add(self, task, depends_on=None):
        """ Adds a new task to the scheduler
        """
        assert task is not None
        name1 = task.__name__
        if hasattr(task, '__self__'):
            name1 += '@0x%x' % id(task.__self__)

        if depends_on:
            if not isinstance(depends_on, (tuple, list)):
                depends_on = [depends_on]

            for task2 in depends_on:
                if task2:
                    name2 = task2.__name__
                    if hasattr(task2, '__self__'):
                        name2 += '@0x%x' % id(task2.__self__)
                    logger.debug('... adding %s (depends on %s)', name1, name2)
                else:
                    logger.debug('... adding %s', name1)
                self._target_tasks.append((task, task2))
        else:
            logger.debug('... adding %s with no dependencies', name1)
            self._target_tasks.append((task, None))

        if self._running:
            self.schedule()

    def append(self, lst):
        """ Appends a list of tasks
        """
        for l in lst:
            if len(l) > 0:
                self.add(l[0], depends_on=l[1:])

    def schedule(self):
        """ Schedule the tasks that must be run
        """
        if self._target_tasks:
            logger.debug('scheduling tasks...')
            tasks_to_run = [t for t in topsort(self._target_tasks) if t]
            self._tasks_to_run = tasks_to_run
        else:
            self._tasks_to_run = []

    def run(self, abort_on_error=False):
        """ Run all the tasks in the order that dependencies need
        """
        self.schedule()

        num_tasks_to_run = len(self._tasks_to_run)
        if num_tasks_to_run == 0:
            logger.info('nothing to do!')
        else:
            logger.debug('%d tasks to run: running!', num_tasks_to_run)
            self._running = True
            while len(self._tasks_to_run) > 0:
                task = self._tasks_to_run.pop()
                if task and task not in self._performed_tasks:
                    try:
                        task()
                    except Exception, e:
                        if abort_on_error:
                            raise SchedulerTaskException(str(e))
                        raise
                    finally:
                        self._performed_tasks.add(task)

            logger.debug('done!')
            self._running = False
            self._performed_tasks = set()

    def clean(self):
        """ Clean the tasks list
        """
        self._target_tasks = []
        self._tasks_to_run = []
        self._performed_tasks = set()

    @property
    def num_completed(self):
        return len(self._performed_tasks)