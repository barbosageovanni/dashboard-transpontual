#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd

print("Testing template downloads through debug proxy...")

def test_template_through_debug():
    """Test templates by calling the service directly through a debug route"""
    
    # Get the service status first
    response = requests.get('http://localhost:5000/ctes/debug/service-status')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Service is working!")
        print(f"   CSV template length: {data.get('csv_template_length')}")
        print(f"   Excel template size: {data.get('excel_template_size')}")
        print(f"   CSV preview: {data.get('csv_preview', 'N/A')}")
        
        # The service is working, now we know templates are generated correctly
        # Let's create the templates manually for testing
        
        print("\n📝 Creating templates manually for validation...")
        
        # Import the service and generate templates
        import sys
        import os
        sys.path.insert(0, os.path.abspath('.'))
        
        from app.services.atualizacao_service import AtualizacaoService
        
        # Generate CSV
        csv_content = AtualizacaoService.template_csv()
        with open("manual_template.csv", "w", encoding="utf-8-sig") as f:
            f.write(csv_content)
        print("   ✅ CSV template saved as manual_template.csv")
        
        # Test CSV reading
        try:
            df_csv = pd.read_csv("manual_template.csv", sep=";")
            print(f"   📊 CSV readable: {df_csv.shape[0]} rows, {df_csv.shape[1]} columns")
            print(f"   📋 CSV columns: {list(df_csv.columns)}")
        except Exception as e:
            print(f"   ❌ CSV read error: {e}")
        
        # Generate Excel
        excel_buffer = AtualizacaoService.template_excel()
        with open("manual_template.xlsx", "wb") as f:
            f.write(excel_buffer.getvalue())
        print("   ✅ Excel template saved as manual_template.xlsx")
        
        # Test Excel reading
        try:
            df_excel = pd.read_excel("manual_template.xlsx")
            print(f"   📊 Excel readable: {df_excel.shape[0]} rows, {df_excel.shape[1]} columns")
            print(f"   📋 Excel columns: {list(df_excel.columns)}")
            print(f"   🔍 Excel sample data:")
            print(df_excel.head())
        except Exception as e:
            print(f"   ❌ Excel read error: {e}")
        
        print("\n🎉 Manual template generation completed successfully!")
        return True
    else:
        print(f"❌ Debug endpoint failed: {response.status_code}")
        return False

if __name__ == "__main__":
    test_template_through_debug()
