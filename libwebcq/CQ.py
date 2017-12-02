#!/usr/bin/evn python

# Author: weichen2046@gmail.com
# Create Date: 2017.12.02

import json
import logging
import re
import urllib
import uuid
import requests


class CQ(object):
    '''
    A helper class for access web ClearQuest.
    '''

    class CQError(Exception):
        '''Basic exception for errors related to use CQ lib.'''

    class SessionError(CQError):
        '''Raised when access network resources without an available session.'''

    def __init__(self, url):
        self.url = url
        self.session = None
        self.cquid = str(uuid.uuid4())

    def open_session(self):
        '''
        You should call `open_session` to acquire a `requests.Session` object
        before call any method that need access network resources.
        '''
        if self.session:
            logging.warning('Session already exist.')

        self.session = requests.Session()

    def close_session(self):
        '''
        You should call `close_session` to release inner `request.Session`
        object when you no need to access network resources.
        '''
        if self.session is None:
            logging.warning('None session exist.')
            return

        self.session.close()

    def check_authenticated(self, cquid=None):
        '''
        Check against the given `cquid` is authenticated or not.

        - Need access network resources.
        - No need login.
        '''
        self._check_session()

        status = 'false'
        is_auth = False

        params = {
            'action': 'CheckAuthenticated',
            'cquid': cquid if cquid else self.cquid,
        }
        path = 'cqlogin.cq'
        url = urllib.parse.urljoin(self.url, path)
        r = self.session.get(url, params=params)
        jobj = self._check_response(r)
        if jobj:
            status = jobj['STATUS']
            is_auth = jobj['isAuthenticated']
        return (status, is_auth)

    def get_db_sets(self):
        '''
        Get available database list.

        - Need access network resources.
        - No need login.
        '''
        self._check_session()

        dbs = []

        path = 'cqlogin.cq'
        params = {
            'action': 'DoGetDbSets',
            'cquid': self.cquid,
        }
        url = urllib.parse.urljoin(self.url, path)
        r = self.session.get(url, params=params)
        jobj = self._check_response(r)
        if jobj:
            for item in jobj['items']:
                dbs.append(item[jobj['identifier']])
        return dbs

    def _check_session(self):
        '''
        Will raise `SessionError` when there is no available session attached.
        '''
        if self.session is None:
            raise CQ.SessionError(
                'Should open session once before access any network resources.')

    def _check_response(self, resp):
        '''
        Return a JSON object or None.
        '''
        jobj = None
        if resp.status_code == requests.codes.ok:
            res_patt = re.compile('for\(;;\);(.*)')
            m = re.match(res_patt, resp.text)
            if m:
                jobj = json.loads(m[1])
        return jobj
