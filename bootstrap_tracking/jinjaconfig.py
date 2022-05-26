from jinja2 import Environment
from django.contrib import messages
from requests import session
import json

def from_json(value):
    return json.loads(value)

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'get_messages': messages.get_messages,
        'request.session': session
        })
    env.filters['from_json'] = from_json
    return env