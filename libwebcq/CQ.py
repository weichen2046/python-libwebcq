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

    path_map = {
        'LOGIN': 'cqlogin.cq',
    }

    def __init__(self, url):
        self.url = url
        self.session = None
        self.cquid = str(uuid.uuid4())
        self.tz_offset = 'GMT+8:00'
        self.userdb = None
        self.full_name = None

    def set_timezone(self, timezone):
        '''
        Set timezone offset. The default timezone offset is `GMT+8:00`.
        '''
        self.tz_offset = timezone

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
        path = self.path_map['LOGIN']
        url = urllib.parse.urljoin(self.url, path)
        resp = self.session.get(url, params=params)
        jobj = self._check_response(resp)
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

        path = self.path_map['LOGIN']
        params = {
            'action': 'DoGetDbSets',
            'cquid': self.cquid,
        }
        url = urllib.parse.urljoin(self.url, path)
        resp = self.session.get(url, params=params)
        jobj = self._check_response(resp)
        if jobj:
            for item in jobj['items']:
                dbs.append(item[jobj['identifier']])
        return dbs

    def login(self, username, password, repository):
        '''
        Login the session.

        - Need access network resources.
        - No need login.
        '''
        self._check_session()
        path = self.path_map['LOGIN']
        url = urllib.parse.urljoin(self.url, path)
        params = {
            'action': 'DoLogin',
        }
        data = {
            'loginId': username,
            'password': password,
            'repository': repository,
            'tzOffset': self.tz_offset,
            'cquid': self.cquid
        }
        resp = self.session.post(url, params=params, data=data)
        if resp.status_code != requests.codes.ok:
            return False
        # Handle non-strict json response
        tmp_text = resp.text.strip()
        tmp_text = re.sub(r"{\s*'?(\w)", r'{"\1', tmp_text)
        tmp_text = re.sub(r",\s*'?(\w)", r',"\1', tmp_text)
        tmp_text = re.sub(r"(\w)'?\s*:(?!/)", r'\1":', tmp_text)
        tmp_text = re.sub(r":\s*'([^']*)'\s*([,}])", r':"\1"\2', tmp_text)
        tmp_text = re.sub(r",\s*]", "]", tmp_text)
        jobj = json.loads(tmp_text)
        if jobj['status'] != 'true':
            return False
        self.cquid = jobj['cqUid']
        self.userdb = jobj['userdb']
        self.full_name = jobj['fullName']
        # TODO: update other inner data if needed.
        return True

    def logout(self):
        '''
        Logout the session.

        - Need access network resources.
        - Need login.
        '''
        self._check_session()
        path = self.path_map['LOGIN']
        url = urllib.parse.urljoin(self.url, path)
        params = {
            'action': 'DoLogout',
        }
        data = {
            'cquid': self.cquid,
        }
        resp = self.session.post(url, params=params, data=data)
        if self._check_response_status(resp):
            self._reset_fields()
            return True
        return False

    def _reset_fields(self):
        self.cquid = str(uuid.uuid4())
        self.userdb = None
        self.full_name = None
        # TODO: reset other inner fields if needed.

    def _check_session(self):
        '''
        Will raise `SessionError` when there is no available session attached.
        '''
        if self.session is None:
            raise CQ.SessionError(
                'Should open session once before access any network resources.')

    def _check_response(self, resp):
        '''
        Assume the response text is starts with `for(;;);` and followed well
        formatted json string.

        Return a JSON object or None.
        '''
        jobj = None
        if resp.status_code == requests.codes.ok:
            res_patt = re.compile(r'for\(;;\);(.*)')
            mat = re.match(res_patt, resp.text)
            if mat:
                jobj = json.loads(mat[1])
        return jobj

    def _check_response_status(self, resp):
        '''
        Helper method for checking network response status.abs

        Return True if status is ok, otherwise False.
        '''
        if resp.status_code == requests.codes.ok:
            return True
        else:
            return False
