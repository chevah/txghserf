Twisted GitHub Service Hooks Server
===================================


A picture is worth a thousand words:

.. figure:: http://adi.roiban.ro/media/img/articles/2013/txghserf.jpg

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

It also include a simple web tool to register hooks or check hook status.
Login using GitHub credentials::

    http://host:port/


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

* Add proper pagination for GitHub API... not it just request 1000 entries.
* Add configuration and checking of secret


Thanks
------

This project is standing on the shoulders of giants:

* Twisted Matrix
* Klein
* AngularJS
* AngujarJS-UI Bootstrap
