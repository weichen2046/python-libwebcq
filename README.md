# python-libwebcq

A wrapper library for accessing web ClearQuest(CQ).

## Dependency python packages

[requests][pip-requests]

```python
pip install requests
```

[nose][pip-nose]

```python
pip install nose
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
