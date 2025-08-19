# Exemplos de Uso - PostgreSQL

## 1. Atualização Básica (Recomendado)
```bash
python bulk_update_cte.py --update-file dados.xlsx --mode empty_only
```

## 2. Preview Antes da Execução
```bash
python bulk_update_cte.py --update-file dados.xlsx --preview-only
```

## 3. Atualização de Todos os Campos
```bash
python bulk_update_cte.py --update-file dados.xlsx --mode all
```

## 4. Lotes Menores (Conexões Lentas)
```bash
python bulk_update_cte.py --update-file dados.xlsx --batch-size 25
```

## 5. Sem Backup (Grandes Volumes)
```bash
python bulk_update_cte.py --update-file dados.xlsx --no-backup
```

## 6. Interface Simplificada
```bash
python quick_run.py
```

## 7. Gerar Template do Banco
```bash
python quick_run.py
# Escolha opção 1
```

## 8. Validar Arquivo
```bash
python quick_run.py
# Escolha opção 3
```

## 9. Estatísticas do Banco
```bash
python quick_run.py
# Escolha opção 4
```

## 10. Exemplo Completo
```bash
python example_postgresql.py
# Escolha opção 1
```
