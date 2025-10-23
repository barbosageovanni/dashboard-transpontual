# 🚀 Guia Rápido - Sistema de Valores Pendentes

## 📍 Localização no Dashboard

O card de **Valores Pendentes** está localizado na segunda linha de métricas do dashboard principal, na segunda posição:

```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard Principal - https://dashboard.transpontual.app.br │
└─────────────────────────────────────────────────────────────┘

Linha 1 (Métricas Principais):
┌────────────┬────────────┬────────────┬────────────┐
│ 💰 Receita │ 📋 CTEs    │ ✅ Processos│ 🚨 Alertas │
│   Total    │   Total    │  Completos │   Ativos   │
└────────────┴────────────┴────────────┴────────────┘

Linha 2 (Métricas Financeiras):
┌────────────┬──────────────┬────────────┬────────────┐
│ 💳 Receita │ ⏳ VALOR A   │ 👥 Clientes│ 📅 Receita │
│ Realizada  │   RECEBER ← │   Ativos   │  Média     │
│            │  [CLIQUE]    │            │   Mensal   │
│            │ ┌──────────┐ │            │            │
│            │ │Ver Lista │ │            │            │
│            │ │  Excel   │ │            │            │
│            │ │   PDF    │ │            │            │
│            │ └──────────┘ │            │            │
└────────────┴──────────────┴────────────┴────────────┘
```

## 🎯 3 Formas de Acessar

### 1️⃣ Clicando no Card Inteiro
```
Clique em qualquer lugar do card "⏳ Valor a Receber"
→ Modal abre automaticamente
```

### 2️⃣ Botão "Ver Lista"
```
Clique no botão azul "📋 Ver Lista"
→ Modal abre com lista completa
```

### 3️⃣ Exportação Direta
```
Clique em "📊 Excel" ou "📄 PDF"
→ Download inicia imediatamente (sem abrir modal)
```

## 📊 Layout do Modal

```
┌────────────────────────────────────────────────────────────────┐
│ ⏳ Valores Pendentes (A Receber)                          [X]  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Filtrar por Cliente: [____________]  [🔍 Filtrar] [🧹 Limpar]│
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 📋 Total de CTEs: 150  💰 Valor Total: R$ 299.367,14    │ │
│  │ 📄 Página: 1 de 3                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─────┬──────────┬──────────┬────────┬───────────┬─────────┐│
│  │ Nº  │  Data    │ Cliente  │ Fatura │   Valor   │  Dias   ││
│  │ CTE │ Emissão  │          │        │           │  Pend.  ││
│  ├─────┼──────────┼──────────┼────────┼───────────┼─────────┤│
│  │12345│10/01/2025│ Cliente A│ F-001  │ R$ 1.500  │ 🔴 95   ││
│  │12346│15/01/2025│ Cliente B│ F-002  │ R$ 2.300  │ 🟡 80   ││
│  │12347│20/01/2025│ Cliente C│ -      │ R$ 1.800  │ 🔵 45   ││
│  │12348│05/02/2025│ Cliente D│ F-003  │ R$ 3.200  │ 🟢 15   ││
│  │ ... │   ...    │   ...    │  ...   │    ...    │  ...    ││
│  └─────┴──────────┴──────────┴────────┴───────────┴─────────┘│
│                                                                │
│  [◀ Anterior]  [1] [2] [3]  [Próximo ▶]                      │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│              [📊 Exportar Excel] [📄 Exportar PDF] [❌ Fechar]│
└────────────────────────────────────────────────────────────────┘
```

## 🎨 Legenda de Cores (Dias Pendentes)

| Cor | Faixa | Status |
|-----|-------|--------|
| 🟢 Verde | 0-30 dias | Normal |
| 🔵 Azul | 31-60 dias | Atenção |
| 🟡 Amarelo | 61-90 dias | Alerta |
| 🔴 Vermelho | 90+ dias | Crítico |

## 📥 Arquivos Exportados

### Excel (.xlsx)
```
valores_pendentes_20251022_143025.xlsx

┌──────────────────────────────────────────────────────────┐
│ Nº CTE │ Data Emissão │ Cliente │ ... │ Dias Pendentes │
├──────────────────────────────────────────────────────────┤
│ 12345  │ 10/01/2025   │ Cliente A│ ... │      95        │
│ 12346  │ 15/01/2025   │ Cliente B│ ... │      80        │
│  ...   │     ...      │   ...    │ ... │     ...        │
├──────────────────────────────────────────────────────────┤
│        │              │  TOTAL:  │     │ R$ 299.367,14  │
└──────────────────────────────────────────────────────────┘
```

### PDF
```
valores_pendentes_20251022_143025.pdf

        Relatório de Valores Pendentes
        Gerado em: 22/10/2025 14:30:25

┌─────────────────────────────────────────────────────────┐
│ Nº CTE │ Data │ Cliente │ Fatura │ Valor │ ... │ Dias │
├─────────────────────────────────────────────────────────┤
│ 12345  │10/01 │Cliente A│ F-001  │R$ ... │ ... │  95  │
│ 12346  │15/01 │Cliente B│ F-002  │R$ ... │ ... │  80  │
│  ...   │ ... │   ...   │  ...   │  ...  │ ... │ ... │
├─────────────────────────────────────────────────────────┤
│        │     │  TOTAL: │        │ R$ 299.367,14        │
└─────────────────────────────────────────────────────────┘
```

## ⚡ Atalhos e Dicas

### Filtros Rápidos
```
1. Digite parte do nome do cliente
2. Pressione Enter (ou clique em Filtrar)
3. A lista atualiza automaticamente
```

### Navegação por Teclado
```
- Tab: navegar entre campos
- Enter: confirmar filtro
- Esc: fechar modal
```

### Exportação com Filtros
```
1. Aplique filtros no modal
2. Clique em "Exportar Excel/PDF"
3. O arquivo exportado respeitará os filtros aplicados
```

## 🔍 Campos da Tabela

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **Nº CTE** | Número do conhecimento | 12345 |
| **Data Emissão** | Data de emissão do CTE | 10/01/2025 |
| **Cliente** | Nome do destinatário | Cliente ABC |
| **Nº Fatura** | Número da fatura (se houver) | F-001 ou - |
| **Valor** | Valor total do CTE | R$ 1.500,00 |
| **Envio Final** | Data do envio final | 15/01/2025 ou - |
| **Dias Pendentes** | Dias sem baixa | 95 (com cor) |
| **Veículo** | Placa do veículo | ABC-1234 |

## 🎯 Casos de Uso Comuns

### Caso 1: Verificar valores atrasados
```
1. Abrir modal
2. Observar badges vermelhos (90+ dias)
3. Entrar em contato com clientes
```

### Caso 2: Gerar relatório mensal
```
1. Clicar em "PDF" diretamente do card
2. Salvar arquivo
3. Enviar para financeiro/diretoria
```

### Caso 3: Acompanhar cliente específico
```
1. Abrir modal
2. Filtrar por nome do cliente
3. Ver todos os CTEs pendentes desse cliente
4. Exportar se necessário
```

### Caso 4: Análise no Excel
```
1. Exportar para Excel
2. Abrir arquivo
3. Criar tabelas dinâmicas
4. Fazer análises personalizadas
```

## ⚠️ Observações Importantes

1. **Atualização Automática**
   - Os dados do card atualizam automaticamente
   - O modal sempre busca dados atualizados ao abrir

2. **Paginação**
   - Mostra 50 registros por página
   - Use navegação para ver todos

3. **Filtros**
   - Filtro por cliente é case-insensitive
   - Busca parcial (não precisa digitar nome completo)

4. **Dias Pendentes**
   - Calculado a partir do envio final (se houver)
   - Ou da data de emissão (fallback)

5. **Valores Zerados**
   - Se mostrar R$ 0,00, não há valores pendentes
   - Parabéns! 🎉

## 📞 Suporte

Dúvidas ou problemas? Entre em contato com o suporte técnico.

---

**Criado em**: 2025-10-22
**Versão**: 1.0.0
**Sistema**: Dashboard Transpontual
