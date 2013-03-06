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

..  warning::
    The JS gui will work fine from localhost, since GitHub API accept all
    localhost origins.
    To allow the JS gui to connect to GitHub from a public server, you will
    need to register the server address as on GitHub OAuth application.


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
* Add proper pagination for GitHub API... not it just request 1000 entries.
* Add configuration and checking of secret


Thanks
------

This project is standing on the shoulders of giants:

* Twisted Matrix
* Klein
* AngularJS
* AngujarJS-UI Bootstrap
* Brandon Sterne for cidr.py
