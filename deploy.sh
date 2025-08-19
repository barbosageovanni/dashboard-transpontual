#!/bin/bash
# Deploy Script - Dashboard Baker Flask

echo "🚀 INICIANDO DEPLOY - Dashboard Baker Flask"
echo "=========================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

# Verificar se PostgreSQL está rodando
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL não encontrado"
    exit 1
fi

# Executar setup
echo "📋 Executando setup completo..."
python3 setup_dashboard.py

# Verificar se setup foi bem-sucedido
if [ $? -eq 0 ]; then
    echo "✅ Setup concluído com sucesso"
    echo ""
    echo "🎯 COMO USAR:"
    echo "   1. Execute: python run.py"
    echo "   2. Acesse: http://localhost:5000"
    echo "   3. Login: admin / senha123"
    echo ""
else
    echo "❌ Erro no setup"
    exit 1
fi