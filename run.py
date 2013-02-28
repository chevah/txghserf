"""
Sample entry point for the server.
"""
from txghserf.server import CONFIGURATION, resource
# Shut the linter.
resource


def handle_event(event):
    """
    Custom code handling events.
    """
    print event

CONFIGURATION['callback'] = handle_event
