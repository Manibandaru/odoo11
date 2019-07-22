
Dynamic Financial Reports
=========================

This module comes under Odoo accounting. It facilitates
the dynamic financial report of balance sheet and
profit ‘n’ loss in both landscape as well as portrait mode.
In the landscape mode, we can configure which section to
appear in the left and which side to appear in the right.
We can drill down from the main report to the journal
entries associated with each accounts .One can open the
form view of each journal entries and view complete details here.

Usage
=====

After the installation, a new menu, 'Dynamic Reports' will be appeared. This menu will open a new wizard where we can select the report,
date duration, type of report, etc.

Configuration
=============

For the landscape mode report, we need to configure the sequence of the reports. From the Accounting -> Configuration ->
Financial Reports ->Account Reports. Report with sequence '0' will be shown in the left side and report with sequence '1'
will be shown in the right side for both the Balance sheet and P & L.
For the portrait mode report, the configuration is similar. Report ordering will be based on the sequence values.
The one with sequence '0' will be arranged first followed by the report with sequence '1'.


Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Contact odoo@cybrosys.com


Contributors
------------

* Linto C.T. <linto@cybrosys.in>

Maintainer
----------

This module is maintained by Cybrosys Technologies.

For support and more information, please visit https://www.cybrosys.com.
