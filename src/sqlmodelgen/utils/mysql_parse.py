'''
to parse mysql uris from cli
'''

from dataclasses import dataclass
from urllib3.util import parse_url

@dataclass
class MySQLURInfo:
    user: str
    psw: str | None
    host: str
    port: int

def parse_mysql(uri: str):
    parsed = parse_url(uri)

    if parsed.scheme != 'mysql':
        raise ValueError('uri provided has not mysql scheme')
    
    auth = parsed.auth
    host = parsed.host
    port = parsed.port

    splauth = auth.split(':')
    if len(splauth) > 2:
        raise ValueError('invalid auth scheme')
    user = splauth[0]
    psw = splauth[1] if len(splauth) == 2 else None

    return MySQLURInfo(
        us
    )