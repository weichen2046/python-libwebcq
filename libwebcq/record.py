#!/usr/bin/evn python

# Author: weichen2046@gmail.com
# Create Date: 2017.12.06

import re


class Record(object):
    '''
    Class for one CQ record.
    '''

    field_parser_map = {
        'ModuleName': 'module_name',
        'State': 'state',
        'LastOpDate': 'last_op_date',
        'OwnerInfo': 'parse_owner_info_field',
        'OpenDuration': 'open_duration',
    }

    def __init__(self, record_id):
        self.display_name = record_id
        self.module_name = None
        self.state = None
        self.last_op_date = None
        self.owner_tel = None
        self.owner_email = None
        self.open_duration = None

    def parse_owner_info_field(self, field):
        '''
        Parser field for owner information.
        '''
        value = field['CurrentValue']
        values = value.split('\r\n')
        self.owner_tel = re.match(r'Tel\s*:\s*(.*)', values[0]).groups()[0]
        self.owner_email = re.match(r'Email\s*:\s*(.*)', values[1]).groups()[0]

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
    def create_from_details_json(jobj):
        '''
        Convert the details json object to a Record instance.

        The json object is parsed from network response.
        '''
        record = Record(jobj['DisplayName'])
        # TODO: transform jobj to Record
        for field in jobj['fields']:
            field_name = field['FieldName']
            if not field_name in record.field_parser_map:
                continue
            parser = record.field_parser_map[field_name]
            if not hasattr(record, parser):
                continue
            if callable(getattr(record, parser)):
                getattr(record, parser)(field)
            else:
                record.common_field_parser(record, parser, field)
        return record
