Twisted GitHub Service Hooks
============================

This is just a boilerplate for implementing a GitHub Service Hooks server
based on Twisted. 

Uses klein and twisted.

Impement your on "run.py" and start it like::

    twistd -n web --class=run.resource

It will parse incomming hooks and covert the JSON into objects.

It is planed to also include a simple web tool to register hooks or check
hook status.
