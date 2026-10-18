#!/usr/bin/env python3
"""
Send one ordinary Python requests call to the local observer.

Start observer.py first. This script targets only the local loopback server,
not a public website. It prints the response and the headers prepared by the
requests library; the observer's server-side record is the main evidence.
"""

import requests


URL = "http://127.0.0.1:8080/demo?source=requests"


def main():
    response = requests.get(URL, timeout=5)

    print("Status:", response.status_code)
    try:
        print("Response:", response.json())
    except ValueError:
        print("Response body:", response.text)

    print("Client-side request headers:")
    sensitive_headers = {"authorization", "cookie", "proxy-authorization"}
    for name, value in response.request.headers.items():
        if name.lower() in sensitive_headers:
            value = "[REDACTED]"
        print(f"{name}: {value}")


if __name__ == "__main__":
    main()
