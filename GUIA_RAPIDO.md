# ⚡ Guia Rápido - Sistema de Controle de Gastos

## 🎯 Visão de 30 Segundos

Um sistema **profissional** que gerencia receitas e despesas com:
- ✅ Pessoas cadastradas com validação de idade
- ✅ Transações com restrição para menores
- ✅ Relatório consolidado de totais
- ✅ Dados persistem automaticamente

---

## ⚙️ Instalação em 3 Passos

### Terminal 1 - Backend
```bash
cd ControladorGastos
dotnet restore
dotnet run
# Rodando em: http://localhost:5000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
# Abrir: http://localhost:3000
```

### Pronto! 🎉
Sistema funcionando com dados persistindo automaticamente.

---

## 📊 O Que o Sistema Faz

### 1️⃣ Aba Pessoas
```
➕ Criar: Nome + Idade
📋 Listar: Todas as pessoas
🗑️ Deletar: Pessoa + suas transações
```

### 2️⃣ Aba Transações
```
➕ Criar: Descrição, Valor, Tipo (Receita/Despesa), Pessoa
📋 Listar: Todas as transações com nome
⚠️ Validação: Menores SÓ podem fazer despesas!
```

### 3️⃣ Aba Relatório
```
👤 Por Pessoa: Receitas | Despesas | Saldo
🏢 Geral: Total Receitas | Total Despesas | Saldo Geral
```

---

## 🔴 Regra Crítica (⚠️ IMPORTANTE)

### Menores de Idade NÃO podem registrar RECEITAS

```
Pessoa: Pedro (15 anos)
├─ ✅ Pode criar DESPESA (ex: gasto com compras)
└─ ❌ NÃO pode criar RECEITA (ex: ganho com trabalho)

Backend bloqueia → Frontend desabilita → BD valida
```

---

## 📁 Arquivos Principais

### Backend (C#)

| Arquivo | Função |
|---------|--------|
| `Controllers/PessoasController.cs` | Rotas de pessoas |
| `Controllers/TransacoesController.cs` | Rotas de transações |
| `Services/PessoaService.cs` | Lógica de pessoas |
| `Services/TransacaoService.cs` | Lógica de transações + VALIDAÇÃO |
| `Models/Pessoa.cs` | Entidade Pessoa |
| `Models/Transacao.cs` | Entidade Transação |
| `Data/ControladorGastosContext.cs` | Banco de dados |

### Frontend (React/TypeScript)

| Arquivo | Função |
|---------|--------|
| `components/CadastroPessoas.tsx` | Gerenciar pessoas |
| `components/CadastroTransacoes.tsx` | Gerenciar transações |
| `components/RelatorioTotais.tsx` | Exibir relatório |
| `services/api.ts` | Comunicação HTTP |
| `types/index.ts` | Interfaces TypeScript |
| `App.tsx` | App principal |

---

## 🔌 API Endpoints

### Pessoas
```
GET    /api/pessoas              # Lista tudo
POST   /api/pessoas              # Cria
DELETE /api/pessoas/{id}         # Deleta (cascata)
```

### Transações
```
GET    /api/transacoes           # Lista tudo
POST   /api/transacoes           # Cria (com validação)
GET    /api/transacoes/totais/resumo  # Relatório
```

---

## 💾 Banco de Dados

**Arquivo**: `controlador-gastos.db` (SQLite)

**Tabelas**:
```
Pessoas
├── Id (PK)
├── Nome
├── Idade
└── DataCriacao

Transacoes
├── Id (PK)
├── Descricao
├── Valor
├── Tipo (Receita/Despesa)
├── PessoaId (FK) → Pessoas
└── DataCriacao
```

**Cascata**: Deletar Pessoa → Deleta suas Transações

---

## ✅ Checklist de Funcionalidades

- [x] Criar pessoa (nome, idade)
- [x] Listar pessoas
- [x] Deletar pessoa
- [x] Criar transação (receita/despesa)
- [x] Listar transações
- [x] Validar menores de idade
- [x] Calcular totais por pessoa
- [x] Exibir totais gerais
- [x] Persistir dados em SQLite
- [x] Interface responsiva
- [x] Código documentado
- [x] Tratamento de erros

---

## 🎨 Stack Visual

```
┌─────────────────────────────────────────┐
│           FRONTEND (React)               │
│   ┌──────────┬─────────┬──────────┐    │
│   │ Pessoas  │ Trans.  │ Relatório│    │
│   └──────────┴─────────┴──────────┘    │
└──────────────┬──────────────────────────┘
               │ HTTP JSON
┌──────────────▼──────────────────────────┐
│    API (ASP.NET Core + C#)               │
│  ┌────────────────────────────────────┐ │
│  │ Controllers → Services → Models    │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │ ORM
┌──────────────▼──────────────────────────┐
│    SQLite Database                       │
│    (controlador-gastos.db)              │
└─────────────────────────────────────────┘
```

---

## 🚨 Erros Comuns

### "API não conecta"
- [ ] Backend rodando em `localhost:5000`?
- [ ] Frontend tentando conectar em `http://localhost:5000`?
- [ ] CORS habilitado?

### "Banco corrupto"
```bash
rm controlador-gastos.db    # Deletar
dotnet run                  # Recria automaticamente
```

### "Pessoa não encontrada"
- Transação está referenciando pessoa inexistente
- Deletar a transação ou pessoa

---

## 💡 Boas Práticas Implementadas

### Backend
- ✅ Separação de Responsabilidades (Controllers, Services, Models)
- ✅ Injeção de Dependências
- ✅ Entity Framework Core com SQLite
- ✅ Validações em múltiplas camadas
- ✅ Async/Await
- ✅ DTOs para comunicação

### Frontend
- ✅ TypeScript com strict mode
- ✅ Componentes reutilizáveis
- ✅ Gerenciamento de estado (useState)
- ✅ Tratamento de erros
- ✅ CSS responsivo (Grid, Flexbox)
- ✅ Validações de frontend

---

## 📞 Próximas Melhorias Sugeridas

1. 🔐 Adicionar autenticação (Login/Senha)
2. 📊 Gráficos (receitas vs despesas)
3. 📅 Filtrar por data
4. 💾 Exportar para PDF/CSV
5. 🏷️ Categorizar transações
6. 🔔 Notificações de alerta
7. 📱 App móvel nativa
8. ☁️ Sincronizar na nuvem

---

## 📚 Documentação Detalhada

Veja `DOCUMENTACAO.md` para:
- Arquitetura completa
- Todos os endpoints
- Fluxo de dados
- Padrões de desenvolvimento
- Exemplos de código

---

## 🎓 Aprendizados-Chave

Este projeto demonstra:
1. **Arquitetura Profissional**: Separação clara de responsabilidades
2. **Validações Rigorosas**: Múltiplas camadas de validação
3. **Boas Práticas C#**: Async, Dependency Injection, SOLID
4. **Boas Práticas React**: Hooks, TypeScript, Components
5. **Dados Persistentes**: SQLite com Entity Framework
6. **Interface Profissional**: CSS responsivo e intuitivo
7. **Documentação Completa**: Código auto-documentado

---

## 🚀 Status do Projeto

```
✅ Backend:   Completo e Funcional
✅ Frontend:  Completo e Funcional
✅ BD:        SQLite Persistente
✅ Testes:    Casos críticos validados
✅ Docs:      Documentação Completa
✅ UX:        Interface Intuitiva

PRONTO PARA PRODUÇÃO! (com algumas melhorias)
```

---

**Desenvolvido com foco em qualidade, clareza e boas práticas.**

Qualquer dúvida, veja `DOCUMENTACAO.md` ou revise o código (tudo está comentado! 📝)
