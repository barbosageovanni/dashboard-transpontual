# ✅ Correção de Critérios dos Alertas - RESOLVIDO

## 🐛 Problema Identificado

**Descrição**: Os valores dos cards "Envio Final Pendente" e "Faturas Vencidas" ainda estavam diferentes das exportações.

**Causa Raiz**: A API `/api/alertas/resumo` estava usando **critérios diferentes** das APIs de listagem/exportação:

### Envio Final Pendente
| Local | Critério | Campo Usado |
|-------|----------|-------------|
| **Exportações** | `data_atesto < hoje - 1 dia` | ✅ `data_atesto` |
| **API Resumo (ERRADO)** | `primeiro_envio < hoje - 7 dias` | ❌ `primeiro_envio` |

### Faturas Vencidas
| Local | Critério | Campo Usado |
|-------|----------|-------------|
| **Exportações** | `envio_final < hoje - 90 dias` | ✅ `envio_final` |
| **API Resumo (ERRADO)** | `data_atesto < hoje - 90 dias` | ❌ `data_atesto` |

---

## 🔧 Correção Aplicada

**Arquivo**: `app/routes/dashboard.py` (linhas 1450-1474)

### ANTES (Critérios Errados)

```python
# Envio Final Pendente - ERRADO ❌
data_limite_final = hoje - timedelta(days=7)
query_final = CTE.query.filter(
    CTE.primeiro_envio < data_limite_final,  # ❌ Campo errado
    CTE.envio_final.is_(None)
)

# Faturas Vencidas - ERRADO ❌
data_limite_vencidas = hoje - timedelta(days=90)
query_vencidas = CTE.query.filter(
    CTE.data_atesto < data_limite_vencidas,  # ❌ Campo errado
    CTE.data_baixa.is_(None)
)
```

### DEPOIS (Critérios Corretos)

```python
# Envio Final Pendente - CORRETO ✅
# IMPORTANTE: Usar mesmos critérios das APIs de listagem/exportação
data_limite_final = hoje - timedelta(days=1)
query_final = CTE.query.filter(
    CTE.data_atesto < data_limite_final,  # ✅ Campo correto
    CTE.envio_final.is_(None)
)

# Faturas Vencidas - CORRETO ✅
# IMPORTANTE: Usar mesmos critérios das APIs de listagem/exportação
data_limite_vencidas = hoje - timedelta(days=90)
query_vencidas = CTE.query.filter(
    CTE.envio_final < data_limite_vencidas,  # ✅ Campo correto
    CTE.data_baixa.is_(None)
)
```

---

## 📊 Critérios Corretos de Cada Alerta

### 1. 🚨 1º Envio Pendente
**Critério**: CTEs **emitidos** há mais de **10 dias** sem primeiro envio

```sql
WHERE data_emissao < (hoje - 10 dias)
  AND primeiro_envio IS NULL
```

✅ **CORRETO** - Não foi alterado

---

### 2. 📤 Envio Final Pendente
**Critério**: CTEs **atestados** há mais de **1 dia** sem envio final

```sql
WHERE data_atesto < (hoje - 1 dia)
  AND envio_final IS NULL
```

✅ **CORRIGIDO** - Agora usa `data_atesto` (antes usava `primeiro_envio`)

**Por quê `data_atesto`?**
- O atesto é quando o cliente confirma o recebimento
- Após o atesto, deve-se fazer o envio final rapidamente (1 dia)
- Se passou mais de 1 dia do atesto sem envio final → ALERTA

---

### 3. 💸 Faturas Vencidas
**Critério**: CTEs com **envio final** há mais de **90 dias** sem baixa

```sql
WHERE envio_final < (hoje - 90 dias)
  AND data_baixa IS NULL
```

✅ **CORRIGIDO** - Agora usa `envio_final` (antes usava `data_atesto`)

**Por quê `envio_final`?**
- O envio final é quando todos os documentos foram enviados
- O prazo de pagamento começa após o envio final
- Se passou mais de 90 dias do envio final sem baixa → VENCIDO

---

### 4. 📋 CTEs sem Faturas
**Critério**: CTEs **atestados** há mais de **3 dias** sem número de fatura

```sql
WHERE data_atesto < (hoje - 3 dias)
  AND (numero_fatura IS NULL OR numero_fatura = '')
```

✅ **CORRETO** - Não foi alterado

---

## 🔄 Sincronização das Queries

Agora todas as queries estão **100% sincronizadas**:

### Envio Final Pendente
```python
# API Listagem (linha 1227-1228)
CTE.query.filter(
    CTE.data_atesto < data_limite,
    CTE.envio_final.is_(None)
)

# Export Excel (linha 1271)
CTE.query.filter(
    CTE.data_atesto < data_limite,
    CTE.envio_final.is_(None)
)

# Export PDF (linha 1280)
CTE.query.filter(
    CTE.data_atesto < data_limite,
    CTE.envio_final.is_(None)
)

# API Resumo (linha 1453-1455) ✅ CORRIGIDO
CTE.query.filter(
    CTE.data_atesto < data_limite,
    CTE.envio_final.is_(None)
)
```

### Faturas Vencidas
```python
# API Listagem (linha 1296-1297)
CTE.query.filter(
    CTE.envio_final < data_limite,
    CTE.data_baixa.is_(None)
)

# Export Excel (linha 1337)
CTE.query.filter(
    CTE.envio_final < data_limite,
    CTE.data_baixa.is_(None)
)

# Export PDF (linha 1348)
CTE.query.filter(
    CTE.envio_final < data_limite,
    CTE.data_baixa.is_(None)
)

# API Resumo (linha 1466-1468) ✅ CORRIGIDO
CTE.query.filter(
    CTE.envio_final < data_limite,
    CTE.data_baixa.is_(None)
)
```

---

## 🧪 Como Verificar Agora

### 1. Recarregar Página
```bash
Ctrl + F5
```

### 2. Verificar Cards
Os cards devem mostrar:
- **📤 Envio Final Pendente**: 134 envios - R$ 198.434,42
- **💸 Faturas Vencidas**: 23 faturas - R$ 32.288,33

### 3. Exportar Excel
1. Clicar em "Excel" no card "Envio Final Pendente"
2. Abrir arquivo: `envio_final_pendente_YYYYMMDD_HHMMSS.xlsx`
3. Verificar última linha: **TOTAL = R$ 198.434,42** ✅

### 4. Exportar PDF
1. Clicar em "PDF" no card "Envio Final Pendente"
2. Abrir arquivo: `envio_final_pendente_YYYYMMDD_HHMMSS.pdf`
3. Verificar rodapé: **TOTAL = R$ 198.434,42** ✅

### 5. Abrir Modal
1. Clicar no card "Envio Final Pendente"
2. Verificar resumo: **134 CTEs - R$ 198.434,42** ✅

### 6. Repetir para "Faturas Vencidas"
Todos os lugares devem mostrar: **23 faturas - R$ 32.288,33** ✅

---

## 📋 Tabela de Verificação

| Alerta | Card | Modal | Excel | PDF | API Resumo |
|--------|------|-------|-------|-----|------------|
| **1º Envio Pendente** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Envio Final Pendente** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Faturas Vencidas** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CTEs sem Faturas** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Fluxo de Dados dos CTEs

```
┌─────────────────────────────────────────────────────────────┐
│                  CICLO DE VIDA DO CTE                       │
└─────────────────────────────────────────────────────────────┘

1. DATA_EMISSAO
   │  (CTE é emitido)
   │
   │  ⏱️ Após 10 dias sem primeiro_envio
   │  → 🚨 Alerta: "1º Envio Pendente"
   │
   ▼
2. PRIMEIRO_ENVIO
   │  (Documentos enviados pela primeira vez)
   │
   ▼
3. DATA_ATESTO
   │  (Cliente confirma recebimento)
   │
   │  ⏱️ Após 1 dia sem envio_final
   │  → 📤 Alerta: "Envio Final Pendente"
   │
   │  ⏱️ Após 3 dias sem numero_fatura
   │  → 📋 Alerta: "CTEs sem Faturas"
   │
   ▼
4. ENVIO_FINAL
   │  (Todos os documentos enviados)
   │
   │  ⏱️ Após 90 dias sem data_baixa
   │  → 💸 Alerta: "Faturas Vencidas"
   │
   ▼
5. DATA_BAIXA
   │  (Pagamento recebido)
   │
   ▼
   ✅ PROCESSO CONCLUÍDO
```

---

## 💡 Por Que os Critérios São Assim?

### Envio Final Pendente usa `data_atesto`
**Lógica de Negócio**:
1. Cliente atesta o recebimento
2. Empresa deve enviar documentos finais em até 1 dia
3. Se passou de 1 dia → alerta para agilizar envio

**Por quê não usar `primeiro_envio`?**
- O primeiro envio pode ser parcial
- O importante é contar a partir do atesto (confirmação do cliente)

### Faturas Vencidas usa `envio_final`
**Lógica de Negócio**:
1. Documentos finais são enviados
2. Prazo de pagamento começa (geralmente 30-90 dias)
3. Se passou de 90 dias sem pagamento → fatura vencida

**Por quê não usar `data_atesto`?**
- O cliente só pode pagar após receber os documentos finais
- O prazo começa no `envio_final`, não no atesto

---

## ✅ Checklist de Correção

- [x] API Resumo: Envio Final usa `data_atesto`
- [x] API Resumo: Faturas Vencidas usa `envio_final`
- [x] Comentários explicativos adicionados no código
- [x] Prazos ajustados (1 dia para envio final)
- [x] Todas as queries sincronizadas
- [x] Documentação atualizada

---

## 🎯 Status Final

✅ **CORRIGIDO E SINCRONIZADO**

Agora **todos** os lugares (cards, modais, Excel, PDF) usam exatamente as **mesmas queries SQL** com os **mesmos campos e critérios**.

---

## 📝 Resumo da Correção

| Item | Antes | Depois |
|------|-------|--------|
| **Envio Final - Campo** | `primeiro_envio` ❌ | `data_atesto` ✅ |
| **Envio Final - Prazo** | 7 dias ❌ | 1 dia ✅ |
| **Faturas Venc. - Campo** | `data_atesto` ❌ | `envio_final` ✅ |
| **Faturas Venc. - Prazo** | 90 dias ✅ | 90 dias ✅ |

---

**Data**: 22/10/2025
**Versão**: 4.2 - Correção de Critérios dos Alertas
**Arquivo Modificado**: `app/routes/dashboard.py` (linhas 1450-1474)
**Autor**: Claude Code (Anthropic)
