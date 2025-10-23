# Sistema de Relatório de Valores Pendentes

## 📋 Descrição

Sistema completo para listar, visualizar e exportar valores pendentes (a receber) no dashboard principal da Transpontual.

## ✨ Funcionalidades Implementadas

### 1. **Card Interativo no Dashboard**
- Card "Valor a Receber" agora é clicável
- Botões de ação integrados:
  - 📋 **Ver Lista**: Abre modal com lista detalhada
  - 📊 **Excel**: Exporta para Excel diretamente
  - 📄 **PDF**: Exporta para PDF diretamente
- Efeito hover com animação suave

### 2. **Modal de Listagem Detalhada**
- Interface moderna e responsiva
- **Filtros**:
  - Filtro por nome do cliente
  - Botões "Filtrar" e "Limpar"
- **Tabela Completa**:
  - Nº CTE
  - Data de Emissão
  - Cliente
  - Nº Fatura
  - Valor Total
  - Data Envio Final
  - Dias Pendentes (com badge colorido por urgência)
  - Veículo
- **Paginação**:
  - 50 registros por página
  - Navegação anterior/próximo
  - Indicação de página atual
- **Resumo em Tempo Real**:
  - Total de CTEs
  - Valor total pendente
  - Número da página atual

### 3. **Sistema de Exportação**

#### **Excel (.xlsx)**
- Planilha formatada profissionalmente
- Cabeçalhos estilizados (fundo azul, texto branco)
- Valores formatados como moeda brasileira
- Linha de total com destaque
- Larguras de coluna otimizadas
- Bordas em todas as células
- Nome do arquivo com timestamp

#### **PDF**
- Layout em paisagem (A4)
- Tabela formatada com:
  - Cabeçalho azul com texto branco
  - Alternância de cores nas linhas
  - Bordas e grid completo
  - Alinhamentos otimizados
- Título e subtítulo com data/hora de geração
- Linha de total destacada
- Suporte para textos longos (truncamento automático)

## 🔌 Endpoints da API

### 1. **Listar Valores Pendentes**
```
GET /dashboard/api/valores-pendentes
```

**Parâmetros**:
- `page` (int, opcional): Número da página (padrão: 1)
- `per_page` (int, opcional): Registros por página (padrão: 50)
- `cliente` (string, opcional): Filtro por nome do cliente

**Resposta**:
```json
{
  "success": true,
  "dados": [...],
  "total_registros": 150,
  "total_valor": 299367.14,
  "pagina_atual": 1,
  "total_paginas": 3,
  "tem_proxima": true,
  "tem_anterior": false
}
```

### 2. **Exportar para Excel**
```
GET /dashboard/api/valores-pendentes/exportar/excel?cliente=Nome
```

### 3. **Exportar para PDF**
```
GET /dashboard/api/valores-pendentes/exportar/pdf?cliente=Nome
```

## 🎨 Indicadores Visuais

### Badges de Dias Pendentes
- 🟢 **Verde** (0-30 dias): Situação normal
- 🔵 **Azul** (31-60 dias): Atenção
- 🟡 **Amarelo** (61-90 dias): Alerta
- 🔴 **Vermelho** (90+ dias): Crítico

## 📁 Arquivos Modificados/Criados

### Backend
- ✅ `app/routes/dashboard.py` (3 novos endpoints)
  - `/api/valores-pendentes`
  - `/api/valores-pendentes/exportar/excel`
  - `/api/valores-pendentes/exportar/pdf`

### Frontend
- ✅ `app/static/js/dashboard.js` (+350 linhas)
  - Módulo completo de valores pendentes
  - 9 funções principais
  - Sistema de modal dinâmico
  - Paginação e filtros
  - Exportação integrada

- ✅ `app/templates/dashboard/index.html`
  - Card de valores pendentes atualizado
  - Botões de ação integrados
  - Evento onclick configurado

- ✅ `app/static/css/dashboard.css`
  - Estilos para hover do card
  - Animações suaves
  - Efeitos de transição

## 🚀 Como Usar

### 1. Visualizar Lista Completa
1. Acesse o dashboard principal
2. Localize o card "⏳ Valor a Receber"
3. Clique no botão "📋 Ver Lista" ou clique no próprio card
4. O modal será aberto com todos os valores pendentes

### 2. Filtrar por Cliente
1. Abra o modal de valores pendentes
2. Digite o nome do cliente no campo de filtro
3. Clique em "Filtrar"
4. Para limpar o filtro, clique em "Limpar"

### 3. Navegar entre Páginas
1. Use os botões "Anterior" e "Próximo"
2. Ou clique diretamente no número da página desejada

### 4. Exportar Relatórios

#### Direto do Card:
- Clique em "📊 Excel" para exportar todos os valores pendentes
- Clique em "📄 PDF" para gerar relatório em PDF

#### Do Modal:
- Aplique filtros se desejar
- Clique em "Exportar Excel" ou "Exportar PDF"
- O arquivo será baixado automaticamente com filtros aplicados

## 🔧 Dependências

### Python
- `Flask`
- `Flask-Login`
- `SQLAlchemy`
- `openpyxl` (Excel)
- `reportlab` (PDF)

### JavaScript
- jQuery
- Bootstrap 5

## 📊 Lógica de Negócio

### Valores Pendentes
São considerados "pendentes" os CTEs que:
- **NÃO** possuem `data_baixa` preenchida
- Ou seja, ainda não foram pagos/baixados

### Cálculo de Dias Pendentes
1. Se existe `envio_final`: usa essa data como referência
2. Caso contrário: usa `data_emissao`
3. Calcula a diferença em dias até hoje

## 💡 Melhorias Futuras (Sugestões)

1. **Filtros Avançados**:
   - Por intervalo de datas
   - Por faixa de valores
   - Por veículo
   - Por faixa de dias pendentes

2. **Ações em Lote**:
   - Marcar múltiplos CTEs como baixados
   - Enviar lembretes automáticos

3. **Gráficos**:
   - Evolução de valores pendentes ao longo do tempo
   - Distribuição por cliente
   - Aging (tempo de pendência)

4. **Notificações**:
   - Alertas para valores com mais de X dias pendentes
   - E-mails automáticos para clientes

5. **Dashboard Específico**:
   - Página dedicada só para valores pendentes
   - Mais estatísticas e análises

## 🐛 Tratamento de Erros

- Validação de dados no backend
- Mensagens de erro claras para o usuário
- Fallbacks para campos vazios/nulos
- Logs detalhados no console
- Toast notifications para feedback visual

## 📝 Notas Técnicas

- Paginação otimizada (SQLAlchemy)
- Queries eficientes (índices em `data_baixa`)
- Formatação de moeda no padrão BR
- Timestamps nos arquivos exportados
- Responsividade mobile-first
- Acessibilidade (ARIA labels)

## ✅ Checklist de Implementação

- [x] Endpoint de listagem com paginação
- [x] Endpoint de exportação Excel
- [x] Endpoint de exportação PDF
- [x] Modal interativo no frontend
- [x] Sistema de filtros
- [x] Paginação funcional
- [x] Botões de ação no card
- [x] Estilos e animações
- [x] Tratamento de erros
- [x] Documentação

---

**Desenvolvido para**: Dashboard Baker - Sistema Transpontual
**Data**: 2025-10-22
**Versão**: 1.0.0
