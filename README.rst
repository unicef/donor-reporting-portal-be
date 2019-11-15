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
| Issue tracker      |https://app.clubhouse.io/stories                    |
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
from unicef_security.tasks import sync_business_area
from donor_reporting_portal.apps.report_metadata.tasks import *

sync_business_area()
grant_sync()
