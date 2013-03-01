Twisted GitHub Service Hooks Server
===================================

This is just a boilerplate for implementing a GitHub Service Hooks server
based on Klein and Twisted.

Implement your on "run.py" and start it like::

    twistd -n web --class=run.resource

It will parse incoming hooks and covert the JSON into objects.

Configure GitHub Hooks using http://host:port/hook/SOME_NAME.

SOME_NAME is just to track the source of the hook.

It is planed to also include a simple web tool to register hooks or check
hook status.

Development
-----------

Get virtual environment and install dependencies::

    make deps

Run the tests::

    make test

Run the server::

    make run
