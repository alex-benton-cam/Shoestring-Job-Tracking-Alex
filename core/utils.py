from datetime import datetime
from dateutil.parser import parse

def stdDateTime(dt=None):
    dt = parse(dt) if dt else datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")