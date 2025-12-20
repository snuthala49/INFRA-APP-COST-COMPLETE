#!/usr/bin/env python3
"""Post a sample payload to the backend /calculate endpoint and print the JSON response."""
import requests
import sys


def main(url="http://127.0.0.1:5001/calculate"):
    payload = {"cpu": 2, "ram": 8, "storage": 100, "network": 10, "backup": 50}
    try:
        r = requests.post(url, json=payload, timeout=5)
        r.raise_for_status()
        print(r.json())
    except Exception as e:
        print("Error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
