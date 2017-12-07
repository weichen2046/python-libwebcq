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

        self.assertTrue(
            found_db, 'Shound contains any predefined database in %s' % mockdata['db_sets'])

    def test_login(self):
        cq = CQ(mockdata['base_url'])
        origin_cquid = cq.cquid
        cq.open_session()
        try:
            res = cq.login(mockdata['loginId'],
                           mockdata['password'], mockdata['repository'])
            status, is_auth = cq.check_authenticated()
        finally:
            cq.close_session()
        self.assertTrue(res, 'Login failed.')
        self.assertNotEqual(origin_cquid, cq.cquid,
                            'New cq uid should be returned after login.')
        self.assertTrue(
            is_auth, 'New cq uid should be authenticated after login.')

        # Clear resources.
        cq.open_session()
        try:
            cq.logout()
        finally:
            cq.close_session()

    def test_logout(self):
        cq = CQ(mockdata['base_url'])
        origin_cquid = cq.cquid
        cq.open_session()
        try:
            res = cq.logout()
            status, is_auth = cq.check_authenticated()
        finally:
            cq.close_session()
        self.assertTrue(res, 'Logout network failed.')
        self.assertNotEqual(origin_cquid, cq.cquid,
                            'New cq uid should be generated after logout.')
        self.assertFalse(
            is_auth, 'New cq uid should not be authenticated after logout.')

    def test_find_record(self):
        cq = CQ(mockdata['base_url'])
        cq.open_session()
        try:
            res = cq.login(mockdata['loginId'],
                           mockdata['password'], mockdata['repository'])
            resource_id = cq.find_record(mockdata['record_id'])
            resource_id2 = cq.find_record(mockdata['record_id2'])
            cq.logout()
        finally:
            cq.close_session()
        self.assertIsNotNone(resource_id)
        self.assertIsNone(resource_id2)

    def test_get_record_details(self):
        cq = CQ(mockdata['base_url'])
        cq.open_session()
        try:
            res = cq.login(mockdata['loginId'],
                           mockdata['password'], mockdata['repository'])
            record = cq.get_cq_record_details(mockdata['record_id'])
            cq.logout()
        finally:
            cq.close_session()

        expect = mockdata['record1']
        self.assertIsNotNone(
            record, 'Record details for %s should not be None.' % mockdata['record_id'])
        self.assertEqual(expect['display_name'], record.display_name,
                         'The fetched record display name should equals the record id.')
        self.assertEqual(expect['module_name'],
                         record.module_name, 'Module name not equal.')
        self.assertEqual(expect['state'], record.state, 'State not equal.')
        self.assertEqual(expect['last_op_date'],
                         record.last_op_date, 'LastOpDate not equal.')
        self.assertEqual(expect['owner_tel'],
                         record.owner_tel, 'Owner tel not equal.')
        self.assertEqual(expect['owner_email'],
                         record.owner_email, 'Owner email not equal.')
        self.assertEqual(expect['open_duration'],
                         record.open_duration, 'OpenDuration not equal.')
