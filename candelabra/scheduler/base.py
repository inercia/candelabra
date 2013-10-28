#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

from candelabra.scheduler.topsort import topsort

logger = getLogger(__name__)


class Task(object):
    """ A callable task
    """

    def __init__(self, c, *args, **kwargs):
        self.fun = None

        if c is not None:
            self.fun = c
            self.args = args
            self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        if self.fun is not None:
            logger.debug('running task function %s', self.fun)
            self.fun(*self.args, **self.kwargs)

    def __repr__(self):
        if self.fun is not None:
            return "<Task %s(%s, %s)>" % (self.fun.__name__, str(self.args), str(self.kwargs))
        else:
            return "<Task empty>"


class Scheduler(object):
    """ A scheduler for tasks
    """

    def __init__(self):
        """ Initialize a scheduler
        """
        self._target_tasks = []
        self._performed_tasks = set()
        self._last_task = Task(None)
        self._running = False

    def add(self, task, depends_on=None):
        """ Adds a new task to the scheduler
        """
        if depends_on:
            if not isinstance(depends_on, (tuple, list)):
                depends_on = [depends_on]

            for task2 in depends_on:
                logger.debug('adding task %s with dependency %s', task, task2)
                self._target_tasks.append((task, task2))
        else:
            logger.debug('adding task %s with terminal dependency', task)
            self._target_tasks.append((task, self._last_task))

        if self._running:
            self.schedule()

    def append(self, lst):
        """ Appends a list of tasks
        """
        for l in lst:
            self.add(l[0], depends_on=l[1:])

    def schedule(self):
        """ Schedule the tasks that must be run
        """
        logger.debug('scheduling tasks...')
        tasks_to_run = topsort(self._target_tasks)
        logger.debug('... %d tasks to run: running', len(tasks_to_run))
        tasks_to_run.reverse()
        self._tasks_to_run = tasks_to_run

    def run(self):
        """ Run all the tasks in the order that dependencies need
        """
        self.schedule()
        self._running = True
        while len(self._tasks_to_run) > 0:
            task = self._tasks_to_run.pop()
            if task not in self._performed_tasks:
                try:
                    task()
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

