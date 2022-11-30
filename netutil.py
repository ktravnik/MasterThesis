#!/usr/bin/env python3

import socket
import sys
import subprocess
import re
from urllib.parse import urlparse

def host_from_url(u: str) ->str:
    try:
        result = urlparse(u)
        return result.hostname
    except:
        return None


def ip_from_hostname(h: str) ->str :
    r = socket.gethostbyname(h)
    return r

def interface_go_out(ip: str) -> str:
    try:
        out = subprocess.run(['ip', 'route', 'get',ip], stdout=subprocess.PIPE).stdout.decode('utf-8')

    except:
        return None
    try:
        x = re.search(r".*dev\s(.*)\ssrc",out)
        c = x.groups(1)[0]
    except:
        return None
    return c

def try_find_if(target: str) -> str:
    result = host_from_url(target)
    if result == None:
        result=target
    try:
        result = ip_from_hostname(result)
    except:
        return None
    return interface_go_out(result)
    

if __name__ == "__main__":
    try:
        url=sys.argv[1]
    except:
        print("Need argument")
    print(try_find_if(url))