#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

print("Testing debug endpoint...")
try:
    response = requests.get('http://localhost:5000/ctes/debug/service-status')
    print(f'Status: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type", "N/A")}')
    print(f'Response length: {len(response.text)}')
    
    # Check if it's JSON or HTML
    if response.headers.get('Content-Type', '').startswith('application/json'):
        print('Response (JSON):')
        print(response.json())
    else:
        print('Response (first 500 chars):')
        print(response.text[:500])
        print('...' if len(response.text) > 500 else '')
        
except Exception as e:
    print(f'Error: {e}')
