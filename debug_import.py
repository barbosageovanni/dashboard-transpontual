#!/usr/bin/env python3

# Test imports step by step
print("Testing step by step import...")

try:
    print("1. Importing pandas...")
    import pandas as pd
    print("   ✅ pandas OK")
except Exception as e:
    print(f"   ❌ pandas failed: {e}")

try:
    print("2. Importing app...")
    from app import db
    print("   ✅ app.db OK")
except Exception as e:
    print(f"   ❌ app.db failed: {e}")

try:
    print("3. Importing CTE model...")
    from app.models.cte import CTE
    print("   ✅ CTE model OK")
except Exception as e:
    print(f"   ❌ CTE model failed: {e}")

try:
    print("4. Importing atualizacao_service module...")
    import app.services.atualizacao_service as service_module
    print(f"   ✅ Module loaded. Contents: {dir(service_module)}")
except Exception as e:
    print(f"   ❌ Module import failed: {e}")

try:
    print("5. Importing AtualizacaoService class...")
    from app.services.atualizacao_service import AtualizacaoService
    print("   ✅ AtualizacaoService class imported successfully!")
except Exception as e:
    print(f"   ❌ Class import failed: {e}")

print("Done.")
