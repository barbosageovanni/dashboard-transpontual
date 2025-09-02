#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

print("Testing various endpoints...")

base_url = "http://localhost:5000"

# Test basic connectivity
print("\n1. Testing basic connectivity...")
try:
    response = requests.get(base_url, timeout=5)
    print(f"   Root URL Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

# Test debug endpoint
print("\n2. Testing debug endpoint...")
try:
    response = requests.get(f"{base_url}/ctes/debug/service-status", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"   Content length: {len(response.text)}")
    
    if 'json' in response.headers.get('Content-Type', ''):
        print("   Response (JSON):")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError as e:
            print(f"   JSON decode error: {e}")
    else:
        print("   Response (first 200 chars):")
        print(f"   '{response.text[:200]}'")
        
except Exception as e:
    print(f"   Error: {e}")

# Test template endpoints directly
print("\n3. Testing template endpoints...")
endpoints = [
    "/ctes/template-atualizacao.csv",
    "/ctes/template-atualizacao.xlsx"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=5)
        print(f"   {endpoint}: {response.status_code}")
        print(f"      Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"      Content-Length: {len(response.content)}")
    except Exception as e:
        print(f"   {endpoint}: Error - {e}")

print("\nDone.")
