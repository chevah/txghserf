"""
This is the part where requests are dispached.
"""
import os

try:
    import json
    # Shut up the linter.
    json
except ImportError:
    import simplejson as json

from klein import resource, route
from twisted.python import log
from twisted.web.static import File

from cidr import get_IP_list

# Shut up the linter.
resource

CONFIGURATION = {
    # Update it from https://api.github.com/meta
    'allow_cidr': [
        '127.0.0.1/24',
        "207.97.227.253/32",
        "50.57.128.197/32",
        "108.171.174.178/32",
        "50.57.231.61/32",
        "204.232.175.64/27",
        "192.30.252.0/22",
        ],
    'callback': None,

    # Cached list of allowed IP address.
    # Expanded at startup based on CIDR.
    # call `expand_allowed_ips()` if `allow_cidr` is changed at runtime.
    '_allowed_ips': {},
}

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')


def expand_allowed_ips():
    """
    Expand the cached list of allowed ips.
    """
    CONFIGURATION['_allowed_ips'] = {}

    for block in CONFIGURATION['allow_cidr']:
        for ip in get_IP_list(block):
            CONFIGURATION['_allowed_ips'][ip] = True

# Do initial expansion.
expand_allowed_ips()


class Event(object):
    """
    Simple container for GitHub Event.
    """
    def __init__(self, hook, name, content):
        self.hook = hook
        self.name = name
        self.content = content

    def __str__(self):
        return """
        hook: %(hook)s
        event: %(event)s
        content:\n%(content)s
            """ % {
        'hook': self.hook,
        'event': self.name,
        'content': self.content,
        }


class ServerException(Exception):
    """
    Generic server exception.
    """
    def __init__(self, message):
        self.message = message


@route('/')
def root(request):
    """
    Entry point.
    """
    return File(STATIC_PATH)


@route('/static', branch=True)
def static(request):
    """
    All files from static.
    """
    return File(STATIC_PATH)


@route('/ping',  methods=['GET'])
def ping(request):
    """
    Simple resource to check that server is up.
    """
    return 'pong'


@route('/hook/<string:hook_name>',  methods=['POST'])
def hook(request, hook_name):
    """
    Main hook entry point.

    Check that request is valid, parse the content and then pass
    the object for further processing.
    """
    if request.getClientIP() not in CONFIGURATION['_allowed_ips']:
        request.code = 403
        log.msg(
            'Receive request for hook "%(name)s" from unauthorized'
            ' "%(ip)s".' % {'name': hook_name, 'ip': request.getClientIP()})
        return "Error:001: Where are you comming from?"

    event_name = request.getHeader('X-Github-Event')
    if not event_name:
        log.msg('No event name for "%(name)s". %(details)s' % {
                'name': hook_name, 'details': request.headers.items()})
        return "Error:004: What event is this?"

    content = None
    try:
        content = parse_request(request, event_name)
    except ServerException, error:
        log.msg('Failed to get json for hook "%(name)s". %(details)s' % {
                'name': hook_name, 'details': error.message})
        return "Error:002: Failed to get hook content."
    except:
        import traceback
        log.msg(
            'Failed to process "%(hook_name)s" "%(event_name)s":\n'
            '%(content)s\n'
            '%(details)s' % {
                'hook_name': hook_name,
                'event_name': event_name,
                'content': content,
                'details': traceback.format_exc(),
                })
        return "Error:003: Internal error"

    event = Event(
        hook=hook_name,
        name=event_name,
        content=content,
        )

    callback = CONFIGURATION['callback']
    if callback:
        callback(event)
    else:
        log.msg("Received new event for %s" % event)


def parse_request(request, event_name):
    """
    Return the event name nad JSON from request.
    """

    SUPPORTED_CONTENT_TYPES = [
        'application/x-www-form-urlencoded',
        'application/json',
        ]

    content_type = request.getHeader('Content-Type')
    if not content_type or content_type not in SUPPORTED_CONTENT_TYPES:
        raise ServerException('Unsuported content type.')

    if content_type == 'application/json':
        json_serialization = request.content.getvalue()
    elif content_type == 'application/x-www-form-urlencoded':
        json_serialization = request.args['payload'][0]
    else:
        raise AssertionError('How did we get here?')

    json_dict = json.loads(json_serialization)
    return json_dict
