# -*- coding: utf-8 -*-
import datetime
import os
import time
import unittest
import uuid

from datetime import (
    datetime,
    timedelta,
)
from malibu.config import configuration
from malibu.util import scheduler
from nose.tools import *


@scheduler.job_store
class TestingJobStore(scheduler.VolatileSchedulerJobStore):

    TYPE = 'testing-volatile'

    def __init__(self, scheduler, *args, **kw):

        super(TestingJobStore, self).__init__(scheduler)

        self.note = None

        if "config" in kw:
            self.initialize(kw.get("config"))

        self._called_with_update = False

    def initialize(self, config):

        self.note = config.get_string("note", None)

    def store(self, job, update=False):

        super(TestingJobStore, self).store(job, update)

        job.metadata.update({"store_updated": True})


class SchedulerTestCase(unittest.TestCase):

    def setUp(self):

        self.scheduler = scheduler.Scheduler()
        try:
            self.scheduler.save_state("testing")
        except NameError:
            self.scheduler.load_state("testing")
        self.result = []

    def __test_raise(self):

        raise Exception("Exception from scheduled function.")

    def schedulerStateCreation_test(self):

        test_func = lambda: True

        job = self.scheduler.create_job(
            name="SchedulerTestCase__creationTest",
            func=test_func,
            delta=timedelta(seconds=1),
            recurring=False)

        s = scheduler.Scheduler()
        s.load_state("testing")

        self.assertIn(
            job.get_name(),
            [j.get_name() for j in s.job_store.get_jobs()])

        self.scheduler.remove_job(job.get_name())

        self.assertNotIn(job.get_name(), s.job_store.get_jobs())

    def schedulerJobTicking_test(self):

        test_id = uuid.uuid4()

        job = self.scheduler.create_job(
            name="SchedulerTestCase__tickingTest",
            func=lambda: self.result.append(test_id),
            delta=timedelta(seconds=1),
            recurring=False)

        time.sleep(1)

        self.assertTrue(job.is_ready(datetime.now()))
        self.scheduler.tick()
        self.assertEqual(self.result.pop(), test_id)

    def schedulerJobRaises_test(self):

        test_id = uuid.uuid4()

        job = self.scheduler.create_job(
            name="SchedulerTestCase__raisesTest",
            func=self.__test_raise,
            delta=timedelta(seconds=1),
            recurring=False)

        job.attach_onfail(lambda job: self.result.append(test_id))

        time.sleep(1)

        self.assertTrue(job.is_ready(datetime.now()))
        self.scheduler.tick()
        self.assertEqual(self.result.pop(), test_id)


class SchedulerJobStoreTestCase(unittest.TestCase):

    def setUp(self):

        self.config = configuration.Configuration()
        self.config.load(os.getcwd() + "/tests/config.txt")

        self.scheduler = scheduler.Scheduler(
            store='testing-volatile',
            config=self.config)
        try:
            self.scheduler.save_state("testing")
        except NameError:
            self.scheduler.load_state("testing")

    def storeConfigLoadingChain_test(self):

        st = self.scheduler.job_store
        self.assertIsNotNone(
            st.note,
            msg="Job store impl. could not initialize from config.")

    def storeUpdatesOnJobChange_test(self):

        test_func = lambda: True

        job = self.scheduler.create_job(
            name="SchedulerJobStoreTestCase__storeUpdatesOnJobChange",
            func=test_func,
            delta=timedelta(seconds=5),
            recurring=False)

        # Calling attach_onfail should trigger a job store update.
        job.attach_onfail(lambda job: job.metadata.update({"failure": True}))

        if not job.metadata.get("store_updated", False):
            self.fail(msg="Job store was not updated properly.")

        st_job = self.scheduler.job_store.get_job(job.get_name())
        if not st_job:
            self.fail(msg="Could not grab job from job store.")

    def storeRemainsStatefullyConsistent_test(self):

        test_func = lambda: True

        job = self.scheduler.create_job(
            name="SchedulerJobStoreTestCase__storeUpdatesOnJobChange",
            func=test_func,
            delta=timedelta(seconds=5),
            recurring=False)

        sch = scheduler.Scheduler(state="testing")

        self.assertIn(job, self.scheduler.job_store.get_jobs())
        self.assertIn(job, sch.job_store.get_jobs())

        sch.remove_job(job.get_name())
