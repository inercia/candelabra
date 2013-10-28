#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import unittest
import logging
from candelabra.scheduler.base import Scheduler

from candelabra.scheduler.topsort import topsort
from candelabra.scheduler.base import Task

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TasksTestSuite(unittest.TestCase):
    def test_tasks_sort(self):
        def some_fun(x, y):
            return x + y

        task1 = Task(some_fun, 1, 1)
        task2 = Task(some_fun, 2, 2)
        task3 = Task(some_fun, 3, 3)
        task4 = Task(some_fun, 4, 4)
        task5 = Task(some_fun, 5, 5)
        task6 = Task(some_fun, 6, 6)

        res = topsort([(task1, task2),
                       (task3, task4),
                       (task5, task6),
                       (task1, task3),
                       (task1, task5),
                       (task1, task6),
                       (task2, task5)])

        logger.info('sorted: %s', str(res))
        self.assertEqual(res, [task1, task2, task3, task5, task4, task6])

    def test_tasks_methods_sort(self):
        def some_fun(x, y):
            return x + y

        class SomeClass(object):
            def some_method(self, x, y):
                return x + y

        o1 = SomeClass()
        o2 = SomeClass()

        task1 = Task(o1.some_method, 1, 1)
        task2 = Task(o2.some_method, 2, 2)
        task3 = Task(some_fun, 3, 3)
        task4 = Task(some_fun, 4, 4)
        task5 = Task(some_fun, 5, 5)
        task6 = Task(some_fun, 6, 6)

        res = topsort([(task1, task2),
                       (task3, task4),
                       (task5, task6),
                       (task1, task3),
                       (task1, task5),
                       (task1, task6),
                       (task2, task5)])

        logger.info('sorted: %s', str(res))
        self.assertEqual(res, [task1, task2, task3, task5, task4, task6])

    def test_tasks_scheduler(self):
        """ Test that the tasks scheduler works
        """
        class Incrementer(object):
            num = 1

            def __init__(self, v):
                self.v = v

            def inc(self):
                logger.debug('incrementing %d by %d', self.v, self.num)
                self.v += self.num

        class Decrementer(object):
            num = 1

            def __init__(self, v):
                self.v = v

            def dec(self):
                logger.debug('decrementing %d by %d', self.v, self.num)
                self.v -= self.num

        inc_1 = Incrementer(0)
        dec_1 = Decrementer(2)

        task_1 = Task(inc_1.inc)
        task_2 = Task(dec_1.dec)
        task_3 = Task(inc_1.inc)
        task_4 = Task(dec_1.dec)
        task_end = Task(None)

        sched = Scheduler()
        sched.add(task_1)
        sched.add(task_2, depends_on=task_1)
        sched.add(task_3, depends_on=task_2)
        sched.add(task_4, depends_on=task_3)
        sched.run()

        self.assertEqual(dec_1.v, 0)
        self.assertEqual(inc_1.v, 2)

        sched.clean()
        inc_1.v = 0
        dec_1.v = 0

        sched.add(task_1)
        sched.add(task_3, depends_on=task_1)
        sched.run()
        self.assertEqual(inc_1.v, 2)
