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

# Shut up the linter.
resource

CONFIGURATION = {
    'allowed_ips': [
        '127.0.0.1',
        '54.235.183.49',
        '54.235.183.23',
        '54.235.118.251',
        '54.235.120.57',
        '54.235.120.61',
        '54.235.120.62',
        ],
    'callback': None,
}

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')


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


@route('/ping',  methods=['GET'])
def ping(request):
    """
    Simple resource to check that server is up.
    """
    return 'pong'


@route('/admin/')
def admin(request):
    return File(STATIC_PATH)


@route('/hook/<string:hook_name>',  methods=['POST'])
def hook(request, hook_name):
    """
    Main hook entry point.

    Check that request is valid, parse the content and then pass
    the object for further processing.
    """
    if not request.getClientIP() in CONFIGURATION['allowed_ips']:
        request.code = 403
        log.msg(
            'Receive request for hook "%(name)s" from unauthorized'
            ' "%(ip)s".' % {'name': hook_name, 'ip': request.getClientIP()})
        return "Error:001: Where are you comming from?"

    event_name = request.getHeader('X-Github-Event')
    if not event_name:
        log.msg(
            'Received hook "%(name)s" for unknown event "%(event_name)s"' % {
                'name': hook_name, 'event_name': event_name})
        return "Error:002: What kind of event is this?"

    event = None
    try:
        content = request.content.read()
        event = Event(
            hook=hook_name,
            name=event_name,
            content=json.loads(content),
            )
    except:
        import traceback
        log.msg('Failed to parse "%(event_name)s":\n%(details)s' % {
            'event_name': event_name, 'details': traceback.format_exc()})
        return "Error:003: Internal error"

    callback = CONFIGURATION['callback']
    if callback:
        callback(event)
    else:
        log.msg("Received new event for %s" % event)
