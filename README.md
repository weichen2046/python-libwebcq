# python-libwebcq

A wrapper library for accessing web ClearQuest(CQ).

## Setup environment

### virtualenv

```bash
cd /project/root/dir
virtualenv -p python3.6 .pyenv
```

## Install dependency python packages

[requests][pip-requests]

```bash
pip install requests
```

[nose][pip-nose]

```bash
pip install nose
```

[demjson][pip-demjson]

```bash
pip install demjson
```

## How to use

```python
cq = CQ('your://webcq/host')
# Open a session befoer any network query.
cq.open_session()
try:
    # Need login before query protected resources.
    res = cq.login('username', 'password', 'repository')
    res_id1 = cq.find_record('record_id_1')
    record1 = cq.get_cq_record_details(res_id1, RecordType.CRP)
    res_id2 = cq.find_record('record_id_2')
    record2 = cq.get_cq_record_details(res_id2, RecordType.CRP)
    # Don't forget logout.
    cq.logout()
finally:
    # Close session when all work done.
    cq.close_session()
```

## How to run unit test

You need setup test configurations before you can run any tests. Just rename `test/unit/test_config_example.py` to `test/unit/test_config.py` and replace all values for each `key` in `mockdata` dictionary according to your real CQ server.

Run all tests:

```bash
nosetests test -v
```

Run single test just like the following:

```bash
nosetests test.unit.test_CQ:CQTestCase.test_get_db_sets -v
```

<!-- links -->
[pip-requests]: http://docs.python-requests.org/en/master/
[pip-nose]: http://nose.readthedocs.io/en/latest/
[pip-demjson]: https://github.com/dmeranda/demjson
