#!/usr/bin/env python3

# Example script #2
import sys
import time

try:
    parameter1 = sys.argv[1]
    parameter2 = sys.argv[2]
    parameter3 = sys.argv[3]
    parameter4 = sys.argv[4]
except:
    desc = """{
    "description": "Hard attack",
    "params": [
        {
            "label": "Timeout",
            "description":"How much time in seconds to wait for server is down",
            "type":"numeric",
            "default": 1,
            "prefix": "-f"
        },
        {
            "label": "Type",
            "description":"Type of attack.",
            "type":"options",
            "options": [
                "http",
                "tcp",
                "https"
            ]
        }
    ]
}"""
    print(desc)  # list all required parameters
    sys.exit(64)

print(f"Run example script #2 with parameters {sys.argv}")
print("Printed immediately.")
time.sleep(2.4)
print("Printed after 2.4 seconds.")