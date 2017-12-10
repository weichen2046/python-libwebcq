#!/usr/bin/env python
'''
Test cases for class libwebcq.CQ.
'''

# Author: weichen2046@gmail.com
# Create Date: 2017.12.02

import unittest

from libwebcq.CQ import CQ
from libwebcq.record import CustomerRecord, ModuleRecord, OwnerInfo, RecordType
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
            resource_id = cq.find_record(mockdata['record_id'])
            record = cq.get_cq_record_details(resource_id, RecordType.CRP)
            cq.logout()
        finally:
            cq.close_session()

        expect = mockdata['record1']
        self.assertIsNotNone(
            record, 'Record details for %s should not be None.' % mockdata['record_id'])
        self.assertEqual(expect['display_name'], record.display_name,
                         'The fetched record display name should equals the record id.')

        # Check module information.
        self.assertIsInstance(record.module, ModuleRecord,
                              'module field should be an instance of ModuleRecord.')
        self.assertEqual(expect['module']['display_name'],
                         record.module.display_name, 'Module name is not equal.')

        self.assertEqual(expect['state'], record.state, 'State is not equal.')
        self.assertEqual(expect['last_op_date'],
                         record.last_op_date, 'LastOpDate is not equal.')

        # Check owner information.
        self.assertIsInstance(record.owner_info, OwnerInfo,
                              'owner_info field should be an instance of OwnerInfo.')
        self.assertEqual(expect['owner_info']['tel'],
                         record.owner_info.tel, 'Owner tel is not equal.')
        self.assertEqual(expect['owner_info']['email'],
                         record.owner_info.email, 'Owner email is not equal.')

        self.assertEqual(expect['open_duration'],
                         record.open_duration, 'OpenDuration is not equal.')

        # Check custom.
        self.assertIsInstance(record.customer, CustomerRecord,
                              'customer field should be an instance of CustomerRecord.')
        self.assertEqual(expect['customer']['display_name'],
                         record.customer.display_name, 'Customer name is not equal.')
        self.assertEqual(expect['customer']['record_id'],
                         record.customer.record_id, 'Customer record id is not equal.')
        self.assertEqual(expect['customer']['stable_location'],
                         record.customer.stable_location, 'Customer stable location is not equal.')

        self.assertEqual(
            expect['version_base_on'], record.version_base_on, 'VersionBaseOn is not equal.')
