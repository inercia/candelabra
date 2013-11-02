#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

from logging import getLogger

logger = getLogger(__name__)


class TaskGenerator(object):
    """ A class that generates tasks
    """
    first_task = object()

    def __init__(self):
        self.clear_tasks()

    def clear_tasks(self):
        self.last_task = None
        self.tasks = []

    def add_task(self, task, depends_on=None):
        if depends_on is not None:
            self.tasks += [(task, depends_on)]
        else:
            self.tasks += [(task, self.first_task)]

        self.last_task = task

    def add_task_seq(self, task, depends_on=None):
        if isinstance(task, list):
            for task1, task2 in task:
                self.add_task_seq(task1, depends_on=task2)

        if self.last_task != task:
            self.tasks += [(task, self.last_task)]
            if depends_on is not None and depends_on != self.last_task:
                self.tasks += [(task, depends_on)]
            self.last_task = task

    def get_tasks(self):
        return self.tasks

