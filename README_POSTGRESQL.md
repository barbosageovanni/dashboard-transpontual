# Sistema de Atualização CTE - PostgreSQL Supabase

## 🚀 Início Rápido

### Execução Simples
```bash
# Linux/Mac
./quick_update.sh meu_arquivo.xlsx

# Windows
quick_update.bat meu_arquivo.xlsx
```

### Execução Avançada
```bash
# Apenas preview
python bulk_update_cte.py --update-file arquivo.xlsx --preview-only

# Modo todos os campos
python bulk_update_cte.py --update-file arquivo.xlsx --mode all

# Lote menor para conexões lentas
python bulk_update_cte.py --update-file arquivo.xlsx --batch-size 50
```

## 📊 Estrutura dos Dados

O sistema trabalha com a tabela `dashboard_baker` existente no Supabase.

### Campos Principais
- `numero_cte`: Identificador único do CTE
- `destinatario_nome`: Nome do cliente/destinatário  
- `veiculo_placa`: Placa do veículo
- `valor_total`: Valor total do frete
- `data_emissao`: Data de emissão do CTE
- `data_baixa`: Data da baixa

### Campos de Processo
- `data_inclusao_fatura`: Data inclusão na fatura
- `data_envio_processo`: Data envio do processo
- `primeiro_envio`: Data do primeiro envio
- `data_rq_tmc`: Data RQ/TMC
- `data_atesto`: Data do atesto
- `envio_final`: Data do envio final

## 🔧 Configuração

### Banco de Dados
O sistema usa as mesmas configurações do projeto Flask:
- Host: db.lijtncazuwnbydeqtoyz.supabase.co
- Porta: 5432
- Banco: postgres
- SSL: Obrigatório

### Modos de Atualização
- `empty_only`: Preenche apenas campos vazios (padrão)
- `all`: Atualiza todos os campos

## 📝 Formato do Arquivo

### Excel/CSV Aceito
```csv
numero_cte,destinatario_nome,valor_total,data_emissao
202410001,Empresa ABC,1500.50,2024-10-01
202410002,Empresa XYZ,2300.75,2024-10-02
```

### Variações de Colunas Aceitas
- CTE, Numero_CTE, CTRC → numero_cte
- Cliente, Destinatario → destinatario_nome  
- Valor, Valor_Frete → valor_total
- Data_Emissao, Data Emissão → data_emissao

## 🛡️ Segurança e Backup

### Backup Automático
- Criado automaticamente antes de cada atualização
- Formato JSON para fácil restauração
- Armazenado em `backups/`

### Validações
- CTEs devem existir no banco
- Formatos de data validados
- Valores numéricos verificados
- Duplicatas detectadas

## 📊 Monitoramento

### Logs
- Logs detalhados em `logs/`
- Rotação automática
- Níveis: INFO, WARNING, ERROR

### Relatórios
- Estatísticas de atualização
- Campos mais modificados
- Performance por lote
- Armazenados em `reports/`

## 🚨 Solução de Problemas

### Erro de Conexão
```bash
# Teste a conexão
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print(db.engine.execute('SELECT 1').scalar())"
```

### Performance Lenta
```bash
# Reduza o tamanho do lote
python bulk_update_cte.py --batch-size 25
```

### CTEs Não Encontrados
```bash
# Verifique total no banco
python -c "from app import create_app; from app.models.cte import CTE; app=create_app(); app.app_context().push(); print(f'Total: {CTE.query.count()}')"
```

## 📞 Suporte

Para suporte, verifique:
1. Logs em `logs/`
2. Configuração em `config/system.json`
3. Conexão com Supabase
4. Estrutura da tabela `dashboard_baker`

Desenvolvido para integração com sistema Baker Dashboard Flask.
