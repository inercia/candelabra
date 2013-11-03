#
# Candelabra
#
# Copyright Alvaro Saurin 2013 - All right Reserved
#

import unittest
import logging
from candelabra.scheduler.base import TasksScheduler

from candelabra.scheduler.topsort import topsort

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TasksTestSuite(unittest.TestCase):
    """ Test suite for tasks and scheduler
    """

    def test_tasks_funs_sort(self):
        """ Testing tha we can sort functions as tasks
        """

        def task1():
            pass

        def task2():
            pass

        def task3():
            pass

        def task4():
            pass

        def task5():
            pass

        def task6():
            pass

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
        """ Testing tha we can sort methods as tasks
        """

        class SomeClass(object):
            def task1(self):
                pass

            def task2(self):
                pass

            def task3(self):
                pass

            def task4(self):
                pass

        def task5():
            pass

        def task6():
            pass

        o1 = SomeClass()

        res = topsort([(o1.task1, o1.task2),
                       (o1.task3, o1.task4),
                       (task5, task6),
                       (o1.task1, o1.task3),
                       (o1.task1, task5),
                       (o1.task1, task6),
                       (o1.task2, task5)])

        logger.info('sorted: %s', str(res))
        self.assertEqual(res, [o1.task1, o1.task2, o1.task3, task5, o1.task4, task6])

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

        sched = TasksScheduler()
        sched.add(inc_1.inc)
        sched.add(dec_1.dec, depends_on=inc_1.inc)
        sched.run()

        self.assertEqual(dec_1.v, 1)
        self.assertEqual(inc_1.v, 1)
