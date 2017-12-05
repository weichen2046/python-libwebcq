#!/usr/bin/evn python

# Author: weichen2046@gmail.com
# Create Date: 2017.12.06


class Record(object):
    '''
    Class for one CQ record.
    '''
    def __init__(self, record_id):
        self.display_name = record_id
        self.module_name = None
        self.state = None

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
            if field_name == 'ModuleName':
                record.module_name = field['CurrentValue']
            if field_name == 'State':
                record.state = field['CurrentValue']
        return record
