#!/usr/bin/env python3

# Example script
import sys

try:
    parameter1 = sys.argv[1]
    parameter2 = sys.argv[2]
    parameter3 = sys.argv[3]
except:
    desc = """{
    "description": "Script Slow DDoS to some servers",
    "params": [
        {
            "label": "Timeout",
            "description":"How much time in seconds to wait for server is down",
            "type":"numeric"
        },
        {
            "label": "Type",
            "description":"Type of attack.",
            "type":"options",
            "options": [
                "http",
                "https"
            ]
        },
        {
            "label": "Static parameter",
            "description":"Some string to send",
            "type":"string",
            "prefix":"-D",
            "value":"200"
        }
    ]
}"""
    print(desc)  # list all required parameters
    sys.exit(64)

print(f"Run example script with parameters {sys.argv}")
