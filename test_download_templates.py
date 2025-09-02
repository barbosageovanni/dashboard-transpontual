#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
from io import BytesIO

def test_template_downloads():
    """Test downloading templates from the running Flask app."""
    base_url = "http://localhost:5000"
    
    print("Testing template downloads from Flask app...")
    
    # Test CSV template download
    print("\n1. Testing CSV template download...")
    try:
        response = requests.get(f"{base_url}/ctes/template-atualizacao.csv")
        if response.status_code == 200:
            csv_content = response.text
            print(f"   ✅ CSV template downloaded successfully ({len(csv_content)} chars)")
            
            # Save and validate
            with open("downloaded_template.csv", "w", encoding="utf-8-sig") as f:
                f.write(csv_content)
            print("   📁 Saved as downloaded_template.csv")
            
            # Test reading
            df = pd.read_csv("downloaded_template.csv", sep=";")
            print(f"   📊 CSV readable: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"   📋 Columns: {list(df.columns)}")
        else:
            print(f"   ❌ CSV download failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ CSV test error: {e}")
    
    # Test Excel template download
    print("\n2. Testing Excel template download...")
    try:
        response = requests.get(f"{base_url}/ctes/template-atualizacao.xlsx")
        if response.status_code == 200:
            excel_content = response.content
            print(f"   ✅ Excel template downloaded successfully ({len(excel_content)} bytes)")
            
            # Save and validate
            with open("downloaded_template.xlsx", "wb") as f:
                f.write(excel_content)
            print("   📁 Saved as downloaded_template.xlsx")
            
            # Test reading
            df = pd.read_excel("downloaded_template.xlsx")
            print(f"   📊 Excel readable: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"   📋 Columns: {list(df.columns)}")
        else:
            print(f"   ❌ Excel download failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Excel test error: {e}")
    
    print("\n🎉 Template download tests completed!")

if __name__ == "__main__":
    test_template_downloads()
