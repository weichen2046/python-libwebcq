#!/usr/bin/env python
'''
Test cases for class libwebcq.CQ.
'''

# Author: weichen2046@gmail.com
# Create Date: 2017.12.02

import unittest

from libwebcq.CQ import CQ
from .test_config import mockdata


class CQTestCase(unittest.TestCase):

    def test_constructor(self):
        noerr = True
        try:
            cq = CQ()
        except TypeError:
            noerr = False

        self.assertFalse(noerr)

    def test_access_net_resoure_without_session(self):
        cq = CQ(mockdata['base_url'])
        with self.assertRaises(CQ.SessionError) as err:
            cq.check_authenticated('cquid')

    def test_check_authenticated(self):
        cq = CQ(mockdata['base_url'])
        cq.open_session()
        try:
            status, is_auth = cq.check_authenticated()
        finally:
            cq.close_session()
        self.assertEqual('true', status)
        self.assertFalse(is_auth)

    def test_get_db_sets(self):
        cq = CQ(mockdata['base_url'])
        cq.open_session()
        try:
            status, is_auth = cq.check_authenticated()
            dbs = cq.get_db_sets()
        finally:
            cq.close_session()
        self.assertEqual('true', status)
        self.assertFalse(is_auth)

        found_db = False
        for db in dbs:
            if db in mockdata['db_sets']:
                found_db = True

        self.assertTrue(found_db, 'Shound contains any predefined database in %s' % mockdata['db_sets'])