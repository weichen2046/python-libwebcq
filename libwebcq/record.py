#!/usr/bin/evn python

# Author: weichen2046@gmail.com
# Create Date: 2017.12.06

from abc import abstractmethod, ABC
from enum import Enum
import re
import sys

from .error import DataTypeError


class OwnerInfo(object):
    '''
    A container for CRP owner information.
    '''

    def __init__(self, tel, email):
        self.tel = tel
        self.email = email


class DataType(Enum):
    '''
    Enum for data type.
    '''
    UNKNOWN = 'UNKNOWN'
    RESOURCE = 'RESOURCE'
    SHORT_STRING = 'SHORT_STRING'
    MULTILINE_STRING = 'MULTILINE_STRING'


class RecordType(Enum):
    '''
    Enum for record type.
    '''
    UNKNOWN = 0
    CRP = 1
    USER = 2
    CUSTOMER = 3
    MODULE = 4


class Record(ABC):
    '''
    Base class for one record of a kind of resource type.
    '''

    _record_type_map = {
        RecordType.CRP: 'CRPRecord',
        RecordType.CUSTOMER: 'CustomerRecord',
        RecordType.USER: 'UserRecord',
        RecordType.MODULE: 'ModuleRecord',
    }

    cq_ref = None
    record_type = RecordType.UNKNOWN
    record_type_res_id = None
    record_id = None
    display_name = None
    stable_location = None
    record_state = None

    @staticmethod
    def common_field_parser(instance, field_name, field):
        '''
        Common field parser.

        After parse, the instance will have attribute named `field_name` and
        it's value will be `field['CurrentValue']`.
        '''
        value = field['CurrentValue']
        data_type = field['DataType']
        if data_type == 'INTEGER':
            value = int(value)
        setattr(instance, field_name, value)

    @staticmethod
    def create_from_json_resp(cq, jobj, record_type):
        '''
        Convert the details json object to a Record instance.

        The json object is parsed from network response.
        '''
        # Create specific record according to record type.
        record_class_name = Record._record_type_map[record_type]
        curr_module = sys.modules[__name__]
        record_class = getattr(curr_module, record_class_name)
        record = record_class()
        # Keep CQ reference for inner usage, e.g. fetch network resources if
        # needed.
        record.cq_ref = cq
        # Parse jobj and fill XXXRecord instance.
        record.parse_jobj(jobj)
        return record

    @staticmethod
    def _check_data_type(field, data_type, msg=''):
        '''
        '''
        dt = field['DataType']
        if dt != data_type.value:
            raise DataTypeError(msg)

    def __init__(self, record_type):
        self.record_type = record_type

    def parse_jobj(self, jobj):
        '''
        Parse common fields.
        '''
        self.record_id = jobj['RecordId']
        self.display_name = jobj['DisplayName']
        self.stable_location = jobj['StableLocation']
        self.record_state = jobj['State']
        self.record_type_res_id = jobj['recordType']
        # Parse type specific fields.
        self.on_parse_jobj(jobj)

    @abstractmethod
    def on_parse_jobj(self, jobj):
        '''
        All subclass should override this method to parse fields specific to
        each type.
        '''
        pass


class CRPRecord(Record):
    '''
    CRP type record.
    '''

    field_parser_map = {
        'ModuleName': 'parse_module_name_field',
        'State': 'state',
        'LastOpDate': 'last_op_date',
        'OwnerInfo': 'parse_owner_info_field',
        'OpenDuration': 'open_duration',
        'Customer': 'parse_customer_field',
        'VersionBaseOn': 'version_base_on',
    }

    def __init__(self):
        super(CRPRecord, self).__init__(RecordType.CRP)
        self.module = None
        self.state = None
        self.last_op_date = None
        self.owner_info = None
        self.open_duration = None
        self.customer = None
        self.version_base_on = None

    def on_parse_jobj(self, jobj):
        for field in jobj['fields']:
            field_name = field['FieldName']
            if not field_name in self.field_parser_map:
                continue
            parser = self.field_parser_map[field_name]
            if not hasattr(self, parser):
                continue
            if callable(getattr(self, parser)):
                getattr(self, parser)(field)
            else:
                self.common_field_parser(self, parser, field)

    def parse_owner_info_field(self, field):
        '''
        Parse field for owner information.
        '''
        value = field['CurrentValue']
        values = value.split('\r\n')
        tel = re.match(r'Tel\s*:\s*(.*)', values[0]).groups()[0]
        email = re.match(r'Email\s*:\s*(.*)', values[1]).groups()[0]
        self.owner_info = OwnerInfo(tel, email)

    def parse_customer_field(self, field):
        '''
        Parse customer information.

        Return an instance of `CustomerRecord`.
        '''
        self._check_data_type(
            field, DataType.RESOURCE, 'Customer field data type should be RESOURCE.')
        record_id = field['RecordId']
        self.customer = self.cq_ref.get_cq_record_details(
            record_id, RecordType.CUSTOMER)

    def parse_module_name_field(self, field):
        '''
        Parse module name information.

        Return an instance of `ModuleRecord`.
        '''
        self._check_data_type(
            field, DataType.RESOURCE, 'Module field data type should be RESOURCE.')
        record_id = field['RecordId']
        self.module = self.cq_ref.get_cq_record_details(record_id, RecordType.MODULE)


class CustomerRecord(Record):
    '''
    Customer type record.
    '''

    def __init__(self):
        super(CustomerRecord, self).__init__(RecordType.CUSTOMER)

    def on_parse_jobj(self, jobj):
        pass


class UserRecord(Record):
    '''
    User type record.
    '''

    def __init__(self):
        super(UserRecord, self).__init__(RecordType.USER)

    def on_parse_jobj(self, jobj):
        pass


class ModuleRecord(Record):
    '''
    Module type record.
    '''

    def __init__(self):
        super(ModuleRecord, self).__init__(RecordType.MODULE)

    def on_parse_jobj(self, jobj):
        pass
