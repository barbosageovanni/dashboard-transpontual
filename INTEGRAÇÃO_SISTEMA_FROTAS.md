# 🚚 Integração Sistema de Frotas + Dashboard Baker

## 🎯 Visão Geral

Este documento descreve a integração completa e segura entre:
- **Sistema de Gestão de Frotas** (FastAPI - Porto 8005)
- **Dashboard Baker Flask** (Faturamento - Porto 5000)

A integração permite **navegação unificada** e **autenticação compartilhada** sem comprometer nenhum sistema existente.

---

## ✅ Status da Implementação

### ✅ **Concluído:**
- [x] Middleware de autenticação JWT compartilhada
- [x] Menu de navegação integrada
- [x] Widget de status no dashboard
- [x] Sincronização de dados em tempo real
- [x] Links SSO entre sistemas
- [x] Verificação de conectividade

### 🔄 **Em Produção:**
- Ambos os sistemas funcionam **independentemente**
- **Zero modificações** em funcionalidades existentes
- Integração é **opcional** e **reversível**

---

## 🔗 Como Funciona

### **1. Autenticação Compartilhada**

```python
# O Dashboard Flask reconhece tokens JWT do sistema de frotas
# Arquivo: app/services/jwt_integration.py

def verificar_autenticacao_jwt():
    token = extract_jwt_from_request()  # Bearer, query param ou cookie
    if token:
        payload = decode_jwt_token(token)
        # Auto-login no Flask se usuário existir
```

### **2. Navegação Integrada**

```html
<!-- Menu dinâmico no Dashboard Flask -->
<!-- Arquivo: app/templates/base.html -->

{% if integration_available %}
    <!-- Menu Sistema de Frotas com indicador de conexão -->
    <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle">
            <i class="fas fa-truck"></i> Sistema de Frotas
            {% if is_jwt_authenticated %}
                <span class="badge bg-success">🔗</span>
            {% endif %}
        </a>
    </li>
{% endif %}
```

### **3. Widget de Status**

```javascript
// Sincronização automática de dados
// Arquivo: dashboard/index.html

function sincronizarDados() {
    Promise.all([
        buscarDadosFrotas('/api/v1/veiculos/count'),
        buscarDadosFrotas('/api/v1/motoristas/count')
    ]).then(([veiculos, motoristas]) => {
        // Atualizar contadores em tempo real
    });
}
```

---

## 🚀 Como Usar

### **Cenário 1: Usuário acessa Sistema de Frotas primeiro**

1. ✅ Faz login no sistema de frotas (localhost:8005)
2. ✅ Recebe token JWT
3. ✅ Navega para Dashboard Faturamento
4. ✅ **Login automático** no Flask (se usuário existir)
5. ✅ Menu mostra "🔗 Conectado"

### **Cenário 2: Usuário acessa Dashboard Flask primeiro**

1. ✅ Faz login normal no Flask (localhost:5000)
2. ✅ Vê menu "Sistema de Frotas"
3. ✅ Clica em links para navegar ao sistema de frotas
4. ✅ Pode fazer login separadamente se necessário

### **Cenário 3: Sistema de Frotas indisponível**

1. ✅ Dashboard Flask continua funcionando normalmente
2. ✅ Menu mostra "⚠️ Sistema Indisponível"
3. ✅ Botão "Tentar Reconectar"
4. ✅ **Zero impacto** nas funcionalidades do Flask

---

## ⚙️ Configuração

### **Variáveis de Ambiente**

```bash
# .env do Dashboard Baker Flask
JWT_SECRET=dev-secret                    # Mesmo secret do sistema de frotas
FROTAS_API_URL=http://localhost:8005    # URL do sistema de frotas
```

### **Arquivos Modificados**

```
dashboard_baker_flask/
├── app/
│   ├── __init__.py                     # ✏️ Middleware JWT integrado
│   ├── services/
│   │   └── jwt_integration.py          # 🆕 Novo módulo de integração
│   └── templates/
│       ├── base.html                   # ✏️ Menu integrado
│       └── dashboard/index.html        # ✏️ Widget de status
└── INTEGRAÇÃO_SISTEMA_FROTAS.md        # 🆕 Esta documentação
```

---

## 🔒 Segurança

### **✅ Medidas Implementadas:**

- **Tokens JWT com expiração** (120 minutos padrão)
- **Verificação de assinatura** (mesmo secret)
- **Fallback gracioso** se sistema indisponível
- **Headers CORS apropriados**
- **Timeout de requisições** (5 segundos)

### **✅ Princípios de Segurança:**

1. **Menor privilégio:** Usuário só acessa o que já tinha permissão
2. **Falha segura:** Se JWT inválido, continua sem autenticação
3. **Auditoria:** Logs de tentativas de autenticação JWT
4. **Isolamento:** Falha em um sistema não afeta o outro

---

## 🛠️ Manutenção

### **Para Atualizar URLs:**

```python
# Alterar apenas esta variável
FROTAS_API_URL = "https://nova-url-producao.com"
```

### **Para Desabilitar Integração:**

```python
# Comentar estas linhas em app/__init__.py
# from app.services.jwt_integration import verificar_autenticacao_jwt
# verificar_autenticacao_jwt()
```

### **Para Debug:**

```bash
# Console do navegador no Dashboard Flask
sincronizarDados()          # Forçar sincronização
verificarConexaoFrotas()    # Testar conectividade
```

---

## 📊 Monitoramento

### **Indicadores de Saúde:**

- 🟢 **Verde:** Sistema conectado e sincronizado
- 🟡 **Amarelo:** Sistema disponível mas não sincronizado
- 🔴 **Vermelho:** Sistema indisponível

### **Logs Importantes:**

```
✅ Usuário autenticado via JWT: username
🔄 Sincronização concluída: {veiculos: 25, motoristas: 15}
⚠️ Sistema de Frotas indisponível
❌ Token JWT inválido ou expirado
```

---

## 🚨 Solução de Problemas

### **"Sistema de Frotas indisponível"**
- ✅ Verificar se o FastAPI está rodando na porta 8005
- ✅ Testar `http://localhost:8005/health`
- ✅ Verificar firewall/antivírus

### **"Login automático não funciona"**
- ✅ Verificar se `JWT_SECRET` é o mesmo nos dois sistemas
- ✅ Verificar se usuário existe com mesmo email/username
- ✅ Verificar se token não expirou

### **"Sincronização falha"**
- ✅ Verificar se usuário tem permissões no sistema de frotas
- ✅ Verificar endpoints: `/api/v1/veiculos/count`, `/api/v1/motoristas/count`
- ✅ Verificar CORS no FastAPI

---

## 🎉 Benefícios da Integração

### **👥 Para Usuários:**
- **Login único** entre sistemas
- **Navegação fluida** sem reautenticação
- **Visão unificada** dos dados
- **Interface consistente**

### **🔧 Para Desenvolvedores:**
- **Zero breaking changes**
- **Sistemas independentes**
- **Fácil manutenção**
- **Escalabilidade mantida**

### **🏢 Para a Empresa:**
- **Produtividade aumentada**
- **Redução de erros**
- **Melhor experiência do usuário**
- **Dados sincronizados**

---

## 📈 Próximos Passos (Opcional)

1. **Sincronização bidirecional** de dados
2. **Dashboard unificado** com dados dos dois sistemas
3. **Notificações push** entre sistemas
4. **Relatórios consolidados**
5. **Migração gradual** para arquitetura única (se desejado)

---

## 🤝 Suporte

Para dúvidas ou problemas:

1. **Verificar logs** no console do navegador
2. **Testar endpoints** manualmente
3. **Verificar configurações** de ambiente
4. **Revisar esta documentação**

---

**✨ Integração implementada com sucesso! Ambos os sistemas continuam funcionando independentemente, mas agora oferecem uma experiência unificada para os usuários.**