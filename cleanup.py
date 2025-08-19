#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de limpeza - PostgreSQL
"""

import os
import shutil
from datetime import datetime, timedelta

def cleanup_files():
    print("🧹 LIMPEZA DO SISTEMA")
    print("="*30)
    
    # Pastas para limpar
    folders_to_clean = {
        'uploads': 7,    # 7 dias
        'logs': 30,      # 30 dias  
        'backups': 60,   # 60 dias
        'reports': 30    # 30 dias
    }
    
    total_removed = 0
    total_size = 0
    
    for folder, days_old in folders_to_clean.items():
        if not os.path.exists(folder):
            continue
            
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    
                    total_removed += 1
                    total_size += file_size
                    
                    print(f"🗑️ Removido: {filepath}")
    
    size_mb = total_size / (1024 * 1024)
    print(f"\n✅ Limpeza concluída:")
    print(f"   Arquivos removidos: {total_removed}")
    print(f"   Espaço liberado: {size_mb:.2f} MB")

if __name__ == "__main__":
    cleanup_files()
