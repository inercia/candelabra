#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger
from candelabra.errors import SchedulerTaskException

from candelabra.scheduler.topsort import topsort, CycleError

logger = getLogger(__name__)


class TasksScheduler(object):
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
        name1 = TasksScheduler.get_task_as_str(task)

        if depends_on:
            if not isinstance(depends_on, (tuple, list)):
                depends_on = [depends_on]

            for task2 in depends_on:
                if task2:
                    name2 = TasksScheduler.get_task_as_str(task2)
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
        try:
            if self._target_tasks:
                logger.debug('scheduling tasks...')
                tasks_to_run = [t for t in topsort(self._target_tasks) if t]
                self._tasks_to_run = tasks_to_run
            else:
                self._tasks_to_run = []
        except CycleError, e:
            logger.critical('cycle error:')
            logger.critical('%s', str(e))
            raise SchedulerTaskException('cycle error')
        except Exception, e:
            logger.critical('uncaught exception when scheduling tasks:')
            logger.debug('target tasks to run:')
            for t in self._target_tasks:
                logger.debug('... task: %s', TasksScheduler.get_task_as_str(t[0]))
            raise
        else:
            logger.debug('... %d required tasks -> %d tasks to run',
                         len(self._target_tasks), len(self._tasks_to_run))
            for t in reversed(self._tasks_to_run):
                assert not isinstance(t, tuple)
                logger.debug('...... task: %s', TasksScheduler.get_task_as_str(t))

    def run(self, abort_on_error=False):
        """ Run all the tasks in the order that dependencies need
        """
        self.schedule()

        self._performed_tasks = set()

        num_tasks_to_run = len(self._tasks_to_run)
        if num_tasks_to_run == 0:
            logger.info('nothing to do!')
        else:
            logger.debug('%d tasks to run: running!', num_tasks_to_run)
            self._running = True
            try:
                while len(self._tasks_to_run) > 0:
                    task = self._tasks_to_run.pop()
                    if task and task not in self._performed_tasks:
                        try:
                            task()
                        except Exception, e:
                            logger.critical('uncaught exception when running in the scheduler:')
                            logger.debug('current task:')
                            logger.debug('... task: %s', TasksScheduler.get_task_as_str(task))
                            logger.debug('pending tasks:')
                            for t in reversed(self._tasks_to_run):
                                logger.debug('... task: %s', TasksScheduler.get_task_as_str(t))

                            if abort_on_error:
                                raise SchedulerTaskException(str(e))
                            raise
                        else:
                            self._performed_tasks.add(task)
            finally:
                logger.debug('executed %d tasks... done!', self.num_completed)
                self._running = False

    def clean(self):
        """ Clean the tasks list
        """
        self._target_tasks = []
        self._tasks_to_run = []
        self._performed_tasks = set()

    @property
    def num_completed(self):
        return len(self._performed_tasks)

    @staticmethod
    def get_task_as_str(task):
        name1 = task.__name__
        if hasattr(task, '__self__'):
            name1 += '@0x%x' % id(task.__self__)
        return name1

