#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
from io import BytesIO

def test_authenticated_downloads():
    """Test downloading templates with authentication."""
    base_url = "http://localhost:5000"
    
    print("Testing authenticated template downloads...")
    
    # Create a session for authentication
    session = requests.Session()
    
    # Login first
    print("\n1. Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'senha123'
    }
    
    # Get login page to get any CSRF tokens if needed
    login_page = session.get(f"{base_url}/login")
    print(f"   Login page status: {login_page.status_code}")
    
    # Attempt login
    login_response = session.post(f"{base_url}/login", data=login_data)
    print(f"   Login response status: {login_response.status_code}")
    
    if login_response.status_code == 200 and 'dashboard' not in login_response.url:
        print("   ❌ Login may have failed")
        return
    
    print("   ✅ Login successful")
    
    # Test CSV template download
    print("\n2. Testing CSV template download...")
    try:
        response = session.get(f"{base_url}/ctes/template-atualizacao.csv")
        print(f"   Response status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {len(response.content)}")
        
        if response.status_code == 200 and 'text/csv' in response.headers.get('Content-Type', ''):
            csv_content = response.text
            print(f"   ✅ CSV template downloaded successfully ({len(csv_content)} chars)")
            
            # Save and validate
            with open("authenticated_template.csv", "w", encoding="utf-8-sig") as f:
                f.write(csv_content)
            print("   📁 Saved as authenticated_template.csv")
            
            # Test reading
            try:
                df = pd.read_csv("authenticated_template.csv", sep=";")
                print(f"   📊 CSV readable: {df.shape[0]} rows, {df.shape[1]} columns")
                print(f"   📋 Columns: {list(df.columns)}")
            except Exception as read_error:
                print(f"   ⚠️  CSV read error: {read_error}")
                # Show first few lines for debugging
                print("   First few lines:")
                lines = csv_content.split('\n')[:3]
                for i, line in enumerate(lines):
                    print(f"      Line {i+1}: {line}")
        else:
            print(f"   ❌ CSV download failed or wrong content type")
    except Exception as e:
        print(f"   ❌ CSV test error: {e}")
    
    # Test Excel template download
    print("\n3. Testing Excel template download...")
    try:
        response = session.get(f"{base_url}/ctes/template-atualizacao.xlsx")
        print(f"   Response status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {len(response.content)}")
        
        if response.status_code == 200 and 'spreadsheet' in response.headers.get('Content-Type', ''):
            excel_content = response.content
            print(f"   ✅ Excel template downloaded successfully ({len(excel_content)} bytes)")
            
            # Save and validate
            with open("authenticated_template.xlsx", "wb") as f:
                f.write(excel_content)
            print("   📁 Saved as authenticated_template.xlsx")
            
            # Test reading
            try:
                df = pd.read_excel("authenticated_template.xlsx")
                print(f"   📊 Excel readable: {df.shape[0]} rows, {df.shape[1]} columns")
                print(f"   📋 Columns: {list(df.columns)}")
            except Exception as read_error:
                print(f"   ⚠️  Excel read error: {read_error}")
        else:
            print(f"   ❌ Excel download failed or wrong content type")
    except Exception as e:
        print(f"   ❌ Excel test error: {e}")
    
    print("\n🎉 Authenticated template download tests completed!")

if __name__ == "__main__":
    test_authenticated_downloads()
