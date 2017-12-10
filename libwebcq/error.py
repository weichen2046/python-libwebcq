#!/usr/bin/evn python

# Author: weichen2046@gmail.com
# Create Date: 2017.12.10


class CQError(Exception):
    '''Basic exception for errors related to use CQ lib.'''


class SessionError(CQError):
    '''Raised when access network resources without an available session.'''


class NeedLoginError(CQError):
    '''Raised when access network resources without login.'''

    def __init__(self):
        super(NeedLoginError, self).__init__('Should login first.')


class DataTypeError(CQError):
    '''
    Raised when data type not match.
    '''
