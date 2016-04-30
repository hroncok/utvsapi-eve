utvsapi-eve
===========

A REST-like read-only API for [ÚTVS ČVUT](https://rozvoj.fit.cvut.cz/Main/rozvrhy-utvs-db)
implemented in [eve](http://python-eve.org/).

To use this, create file named `mysql.cnf` with your MySQL credentials, see an example here:

    [client]
    host = localhost
    user = username
    database = dbname
    password = insecurepassword

This has been developed and run on Python 3 only, legacy Python might not work.

Install `eve`, `eve-sqlalchemy` and `mysqlclient` (you'll need mysql devel package for that). You might do it with virtualenv:

    pyvenv venv
    . venv/bin/activate
    pip install eve eve-sqlalchemy mysqlclient

You'll also need `eve-docs`, unfortunately the version on PyPI has a Python 3 incompatible print statement, which has been fixed in git, but not released yet.

    pip install https://github.com/charlesflynn/eve-docs/archive/master.zip

Start the service in debug mode:

    PYTHONPATH=. python3 utvsapi/main.py

Or run with gunicorn:

    pip install gunicorn
    PYTHONPATH=. gunicorn utvsapi.main:app

License
-------

This software is licensed under the terms of the MIT license, see LICENSE for full text and copyright information.
