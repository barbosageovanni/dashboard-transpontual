#!/bin/bash
# Script de execução rápida - PostgreSQL

echo "🚀 SISTEMA DE ATUALIZAÇÃO CTE - POSTGRESQL"
echo "========================================="

# Verifica se está no diretório correto
if [ ! -f "bulk_update_cte.py" ]; then
    echo "❌ Execute este script no diretório do sistema de atualização"
    exit 1
fi

# Verifica arquivo de atualização
if [ -z "$1" ]; then
    echo "📄 Uso: $0 <arquivo_excel>"
    echo "Exemplo: $0 atualizacoes.xlsx"
    exit 1
fi

ARQUIVO="$1"
MODO="${2:-empty_only}"
BATCH="${3:-100}"

if [ ! -f "$ARQUIVO" ]; then
    echo "❌ Arquivo não encontrado: $ARQUIVO"
    exit 1
fi

echo "📋 Configuração:"
echo "  - Arquivo: $ARQUIVO"
echo "  - Modo: $MODO"
echo "  - Lote: $BATCH"
echo ""

# Executa com preview primeiro
echo "👁️ Preview das alterações:"
python bulk_update_cte.py --update-file "$ARQUIVO" --mode "$MODO" --preview-only

echo ""
read -p "▶️ Executar atualizações? (s/N): " CONFIRMA

if [[ $CONFIRMA =~ ^[Ss]$ ]]; then
    echo "🔄 Executando atualizações..."
    python bulk_update_cte.py --update-file "$ARQUIVO" --mode "$MODO" --batch-size "$BATCH"
else
    echo "❌ Execução cancelada"
fi
