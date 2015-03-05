GitHub Service Hooks Server based on Twisted
============================================

This is just a boilerplate for implementing a GitHub Service Hooks server
based on Klein and Twisted.

Implement your on "run.py" and start it like::

    twistd -n web --class=run.resource

It will parse incoming hooks and return an 'Event' containing hook name,
event name and JSON payload.

Configure GitHub Hooks using::

    http://host:port/hook/HOOK-NAME

HOOK-NAME is just a random string to track the source of the hook or
implement multiple hooks on the same server.


Hooks registration (obsolete)
-----------------------------

It also include a simple web tool to register hooks or check hook status.

It was created by the time when GitHub Settings page did not provide a GUI
for configuring HTTP hooks but now GitHub Settings page is usage and you
should use it instead.


Development
-----------

Get virtual environment and install dependencies::

    make deps

Run the tests::

    make test

Run the server::

    make run


TODO
----

* Add ssl security check instead of IP filter.
* Add configuration and checking of secret


Thanks
------

This project is standing on the shoulders of giants:

* Twisted Matrix
* Klein
* AngularJS
* AngujarJS-UI Bootstrap
* Brandon Sterne for cidr.py
