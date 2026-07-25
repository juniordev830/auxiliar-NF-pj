# 📚 Documentação - Sistema de Controle de Gastos Residenciais

## 🎯 Visão Geral

Sistema completo para gerenciamento de receitas e despesas residenciais, desenvolvido com:
- **Backend**: ASP.NET Core (.NET 8) com C#
- **Frontend**: React com TypeScript
- **Banco de Dados**: SQLite (persistência local)

---

## 📋 Tabela de Conteúdos

1. [Arquitetura do Sistema](#arquitetura-do-sistema)
2. [Instalação e Execução](#instalação-e-execução)
3. [Funcionalidades Implementadas](#funcionalidades-implementadas)
4. [Regras de Negócio](#regras-de-negócio)
5. [Estrutura de Pastas](#estrutura-de-pastas)
6. [API Endpoints](#api-endpoints)
7. [Fluxo de Dados](#fluxo-de-dados)
8. [Padrões e Boas Práticas](#padrões-e-boas-práticas)

---

## 🏗️ Arquitetura do Sistema

### Camadas da Aplicação

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  Componentes, Estado, Interface do Usuário             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
┌────────────────────▼────────────────────────────────────┐
│                   API (ASP.NET Core)                    │
│  Controllers, Services, DTOs, Validações              │
└────────────────────┬────────────────────────────────────┘
                     │ Entity Framework Core
┌────────────────────▼────────────────────────────────────┐
│                 Banco de Dados (SQLite)                │
│  Tabelas: Pessoas, Transações                         │
└─────────────────────────────────────────────────────────┘
```

### Padrão MVC/Service Layer

- **Controllers**: Recebem requisições HTTP e chamam serviços
- **Services**: Contêm a lógica de negócio (validações, cálculos)
- **Models**: Entidades do banco de dados
- **DTOs**: Transferência de dados entre camadas
- **DbContext**: Gerenciamento do banco de dados

---

## 🚀 Instalação e Execução

### Pré-requisitos

- .NET 8 SDK instalado
- Node.js 16+ e npm/yarn instalados
- Git

### Backend (ASP.NET Core)

```bash
# Navegar para a pasta do backend
cd ControladorGastos

# Restaurar dependências
dotnet restore

# Executar a aplicação
dotnet run

# A API estará disponível em: http://localhost:5000
```

### Frontend (React)

```bash
# Navegar para a pasta do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# A aplicação estará disponível em: http://localhost:3000
```

### Usar a Aplicação

1. Abrir http://localhost:3000 no navegador
2. Navegar entre as abas: Pessoas, Transações, Relatório de Totais
3. Os dados são persistidos automaticamente no banco de dados SQLite

---

## ✨ Funcionalidades Implementadas

### 1. Cadastro de Pessoas ✅
- **Criar**: Nome e idade (validação de range 0-150)
- **Listar**: Todas as pessoas com informações básicas
- **Deletar**: Remove pessoa e TODAS suas transações (cascata)
- **Validação**: Nome obrigatório, idade válida

### 2. Cadastro de Transações ✅
- **Criar**: Descrição, valor, tipo (Receita/Despesa), pessoa
- **Listar**: Todas as transações com nome da pessoa
- **Validação**:
  - Pessoa deve existir no sistema
  - Valor deve ser positivo
  - **CRÍTICO**: Menores de idade (< 18 anos) SÓ podem registrar DESPESAS
- **Tipos**:
  - Receita (1): Entradas de recursos
  - Despesa (2): Saídas de recursos

### 3. Consulta de Totais ✅
- **Por Pessoa**:
  - Total de Receitas
  - Total de Despesas
  - Saldo (Receitas - Despesas)
- **Geral do Sistema**:
  - Total geral de Receitas
  - Total geral de Despesas
  - Saldo Líquido Geral
- **Formatação**: Moeda brasileira (R$)

---

## 📏 Regras de Negócio

### ✋ Restrição de Menores de Idade (CRÍTICA)

**Regra**: Pessoas menores de 18 anos **SÓ** podem registrar **DESPESAS**

**Implementação**:
1. **Backend**: Validação em `TransacaoService.CriarTransacaoAsync()`
2. **Frontend**: Desabilitação de opção "Receita" e aviso visual
3. **Banco de Dados**: Validação de dados no modelo

```csharp
// Validação no serviço
if (!pessoa.EhMaiorDeIdade() && dto.Tipo == TipoTransacao.Receita)
{
    throw new ArgumentException(
        $"A pessoa '{pessoa.Nome}' é menor de idade ({pessoa.Idade} anos) " +
        $"e portanto não pode registrar receitas. Apenas despesas são permitidas."
    );
}
```

### 🗑️ Cascata de Deleção

**Regra**: Ao deletar uma pessoa, todas suas transações são deletadas

**Implementação**:
- DbContext: `OnDelete(DeleteBehavior.Cascade)` configurado na relação
- Banco de Dados: Constraint de foreign key com ON DELETE CASCADE

### 💾 Persistência de Dados

**Armazenamento**:
- Arquivo SQLite: `controlador-gastos.db` na raiz do projeto
- Dados mantidos após fechar a aplicação
- Automático com Entity Framework Core

---

## 📁 Estrutura de Pastas

### Backend

```
ControladorGastos/
├── Controllers/
│   ├── PessoasController.cs      # Endpoints de pessoas
│   └── TransacoesController.cs   # Endpoints de transações
├── Models/
│   ├── Pessoa.cs                # Modelo de Pessoa
│   └── Transacao.cs             # Modelo e Enum de Transação
├── Data/
│   └── ControladorGastosContext.cs  # DbContext (mapeamento)
├── Services/
│   ├── IPessoaService.cs        # Interface do serviço
│   ├── PessoaService.cs         # Implementação
│   ├── ITransacaoService.cs     # Interface do serviço
│   └── TransacaoService.cs      # Implementação (lógica de negócio)
├── DTOs/
│   ├── PessoaDTO.cs             # DTOs de Pessoa
│   ├── TransacaoDTO.cs          # DTOs de Transação
│   └── TotaisDTO.cs             # DTOs de Totais
├── Program.cs                   # Configuração e startup
├── ControladorGastos.csproj     # Arquivo de projeto
└── controlador-gastos.db        # Banco de dados SQLite
```

### Frontend

```
frontend/
├── src/
│   ├── components/
│   │   ├── CadastroPessoas.tsx       # Componente de pessoas
│   │   ├── CadastroTransacoes.tsx    # Componente de transações
│   │   └── RelatorioTotais.tsx       # Componente de relatório
│   ├── services/
│   │   └── api.ts                    # Serviço HTTP (axios)
│   ├── types/
│   │   └── index.ts                  # Interfaces TypeScript
│   ├── styles/
│   │   ├── Cadastro.css              # Estilos de cadastro
│   │   └── RelatorioTotais.css       # Estilos do relatório
│   ├── App.tsx                       # Componente principal
│   ├── App.css                       # Estilos principais
│   └── main.tsx                      # Ponto de entrada
├── index.html                        # HTML root
├── vite.config.ts                    # Configuração do Vite
├── tsconfig.json                     # Configuração TypeScript
├── tsconfig.node.json                # TypeScript para Node
└── package.json                      # Dependências npm
```

---

## 🔌 API Endpoints

### Pessoas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/pessoas` | Lista todas as pessoas |
| GET | `/api/pessoas/{id}` | Obtém uma pessoa específica |
| POST | `/api/pessoas` | Cria uma nova pessoa |
| DELETE | `/api/pessoas/{id}` | Deleta uma pessoa (cascata) |

**Exemplo POST**:
```json
{
  "nome": "João Silva",
  "idade": 30
}
```

### Transações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/transacoes` | Lista todas as transações |
| GET | `/api/transacoes/pessoa/{pessoaId}` | Transações de uma pessoa |
| POST | `/api/transacoes` | Cria uma nova transação |
| GET | `/api/transacoes/totais/resumo` | Obtém relatório de totais |

**Exemplo POST**:
```json
{
  "descricao": "Salário",
  "valor": 3000.00,
  "tipo": 1,
  "pessoaId": 1
}
```

**Tipos de Transação**:
- `1` = Receita
- `2` = Despesa

---

## 🔄 Fluxo de Dados

### Criar Pessoa

```
Frontend (CadastroPessoas)
    ↓ POST /api/pessoas
Backend (PessoasController)
    ↓ Chama
PessoaService.CriarPessoaAsync()
    ├─ Valida dados
    └─ Persiste no DbContext
    ↓ Salva no SQLite
Frontend (recebe PessoaResponseDTO)
    ↓
Atualiza lista e aviso de sucesso
```

### Criar Transação

```
Frontend (CadastroTransacoes)
    ↓ POST /api/transacoes
Backend (TransacoesController)
    ↓ Chama
TransacaoService.CriarTransacaoAsync()
    ├─ Valida existência da pessoa
    ├─ CRÍTICO: Valida restrição de menores
    ├─ Valida dados
    └─ Persiste no DbContext
    ↓ Salva no SQLite
Frontend (recebe TransacaoResponseDTO)
    ↓
Atualiza lista e aviso de sucesso
```

### Obter Relatório de Totais

```
Frontend (RelatorioTotais - mounted)
    ↓ GET /api/transacoes/totais/resumo
Backend (TransacoesController)
    ↓ Chama
TransacaoService.ObterResumoTotaisAsync()
    ├─ Busca todas as pessoas
    ├─ Para cada pessoa:
    │   ├─ Soma receitas
    │   ├─ Soma despesas
    │   └─ Calcula saldo
    └─ Calcula totais gerais
Frontend (recebe ResumoTotaisDTO)
    ↓
Renderiza cards de pessoas e resumo geral
```

---

## 📐 Padrões e Boas Práticas

### 1. Separação de Responsabilidades
- **Controllers**: Apenas roteamento HTTP
- **Services**: Lógica de negócio
- **Models**: Dados
- **DTOs**: Comunicação entre camadas

### 2. Injeção de Dependências
```csharp
// Registrado em Program.cs
builder.Services.AddScoped<IPessoaService, PessoaService>();
builder.Services.AddScoped<ITransacaoService, TransacaoService>();
```

### 3. Validação em Múltiplas Camadas
- **Frontend**: Validação imediata ao usuário
- **Serviço**: Validação de regras de negócio
- **Banco de Dados**: Constraints de integridade

### 4. Tratamento de Erros
```csharp
try
{
    // Operação
}
catch (ArgumentException ex)
{
    return BadRequest(new { mensagem = ex.Message });
}
```

### 5. Documentação em Código
- Comentários XML em métodos públicos
- Explicação de lógicas complexas
- Blocos de comentários para seções

### 6. TypeScript Strict Mode
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### 7. Formatação de Dados
- Moeda: Locale brasileiro (R$)
- Datas: Formato DD/MM/YYYY
- Valores monetários: 2 casas decimais

### 8. Async/Await
```csharp
public async Task<List<Pessoa>> ListarPessoasAsync()
{
    return await _context.Pessoas.ToListAsync();
}
```

---

## 🧪 Casos de Teste Importantes

### Menor de Idade Tentando Registrar Receita
- ✅ **Esperado**: Erro 400 com mensagem clara
- ✅ **Implementado**: Validação em `TransacaoService`

### Deletar Pessoa com Transações
- ✅ **Esperado**: Pessoa deletada + todas suas transações deletadas
- ✅ **Implementado**: Cascata no DbContext

### Criar Pessoa com Dados Inválidos
- ✅ **Esperado**: Validação de nome e idade
- ✅ **Implementado**: No serviço e no controller

### Criar Transação com Pessoa Inexistente
- ✅ **Esperado**: Erro 400
- ✅ **Implementado**: Verifica existência primeiro

---

## 🔐 Segurança

### Validações Implementadas
1. ✅ Validação de entrada em todos os endpoints
2. ✅ Mensagens de erro sem expor detalhes internos
3. ✅ CORS configurado para aceitar requests locais
4. ✅ Tipos TypeScript para segurança em tempo de compilação

### Recomendações para Produção
1. Adicionar autenticação (JWT, OAuth)
2. Usar HTTPS
3. Validar e sanitizar entrada HTML
4. Implementar rate limiting
5. Adicionar logs de auditoria
6. Usar variáveis de ambiente para configurações

---

## 📝 Notas de Desenvolvimento

### Banco de Dados
- SQLite: arquivo local sem configuração externa
- Migrations: Use `dotnet ef database update` se adicionar migrations
- Seed: Dados iniciais podem ser adicionados em `Program.cs`

### Frontend
- Hot Reload: Vite recarrega automaticamente em desenvolvimento
- TypeScript: Compilado em tempo de build
- Axios: Lib HTTP com interceptores para tratamento de erros

### Execução Simultânea
```bash
# Terminal 1
cd ControladorGastos && dotnet run

# Terminal 2
cd frontend && npm run dev
```

---

## 📞 Suporte e Melhorias Futuras

### Melhorias Sugeridas
1. Autenticação de usuários
2. Backup automático do banco de dados
3. Exportar dados para CSV/PDF
4. Categorização de transações
5. Gráficos e análises
6. Filtros por data
7. Busca e paginação

### Troubleshooting

**API não conecta**:
- Verificar se ASP.NET está rodando em localhost:5000
- Verificar CORS em Program.cs

**Frontend não conecta na API**:
- Verificar URL em `api.ts`: deve ser http://localhost:5000
- Verificar se backend está rodando

**Banco de dados corrompido**:
- Deletar arquivo `controlador-gastos.db`
- Reiniciar a aplicação (recriará o banco)

---

## 📄 Licença

Este projeto foi desenvolvido como teste técnico.

---

**Desenvolvido com ❤️ usando .NET e React**
