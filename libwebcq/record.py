#!/usr/bin/evn python

# Author: weichen2046@gmail.com
# Create Date: 2017.12.06

from abc import abstractmethod, ABC
from enum import Enum
import re
import sys


class RecordType(Enum):
    '''
    Enum for record type.
    '''
    UNKNOWN = 0
    CRP = 1
    USER = 2
    CUSTOMER = 3


class Record(ABC):
    '''
    Base class for one record of a kind of resource type.
    '''

    _record_type_map = {
        RecordType.CRP: 'CRPRecord',
        RecordType.CUSTOMER: 'CustomerRecord',
        RecordType.USER: 'UserRecord',
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
        'ModuleName': 'module_name',
        'State': 'state',
        'LastOpDate': 'last_op_date',
        'OwnerInfo': 'parse_owner_info_field',
        'OpenDuration': 'open_duration',
        'Customer': 'parse_customer_field',
    }

    def __init__(self):
        super(CRPRecord, self).__init__(RecordType.CRP)
        self.module_name = None
        self.state = None
        self.last_op_date = None
        self.owner_tel = None
        self.owner_email = None
        self.open_duration = None
        self.customer = None

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
        self.owner_tel = re.match(r'Tel\s*:\s*(.*)', values[0]).groups()[0]
        self.owner_email = re.match(r'Email\s*:\s*(.*)', values[1]).groups()[0]

    def parse_customer_field(self, field):
        '''
        Parse customer information.

        Return an instance of `CustomerRecord`.
        '''
        data_type = field['DataType']
        if data_type != 'RESOURCE':
            return
        record_id = field['RecordId']
        self.customer = self.cq_ref.get_cq_record_details(
            record_id, RecordType.CUSTOMER)


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
