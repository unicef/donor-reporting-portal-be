ABOUT Donor Reporting Portal
============================


Links
-----

+--------------------+----------------+--------------+--------------------+
| Stable             |                | |master-cov| |                    |
+--------------------+----------------+--------------+--------------------+
| Development        |                | |dev-cov|    |                    |
+--------------------+----------------+--------------+--------------------+
| Source Code        |https://github.com/unicef/donor-reporting-portal    |
+--------------------+----------------+-----------------------------------+


.. |master-cov| image:: https://circleci.com/gh/unicef/etools/tree/master.svg?style=svg
                    :target: https://circleci.com/gh/unicef/aaa/tree/master


.. |dev-cov| image:: https://circleci.com/gh/unicef/etools/tree/develop.svg?style=svg
                    :target: https://circleci.com/gh/unicef/aaa/tree/develop





Troubleshoot
--------------------
*  Exception are logged in Sentry: https://sentry.io/unicef-jk/
*  Each container in Rancher allows to access local logs


Get Started
--------------------
* populate your .env file from template .env_template
* python manage.py upgrade --all


Development Release
--------------------
init version
* update requirements (sys - python)
* `make build-base`

develop features
* develop features
* `make build release`

finish version
* `git flow release start`
* update CHANGES
* update version (__init__.py)
* update makefile version
