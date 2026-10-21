# 💰 Sistema de Controle de Gastos Residenciais

Um sistema completo e profissional para gerenciar receitas e despesas residenciais, com validações rigorosas e interface intuitiva.

> **Estado do repositório:** esta versão publicada contém a documentação do projeto. O código da aplicação (pasta `ControladorGastos` e pasta `frontend`) precisa ser versionado para que a execução descrita abaixo seja reproduzível por outras pessoas.

## ✅ Checklist para a próxima publicação

- [ ] Adicionar o backend ASP.NET Core em `ControladorGastos/`.
- [ ] Adicionar o frontend React em `frontend/`.
- [ ] Incluir o arquivo de solução `.sln` e os projetos `.csproj`.
- [ ] Adicionar um exemplo de configuração sem credenciais reais.
- [ ] Confirmar as portas da API e do frontend na documentação.

## ✨ Características Principais

✅ **Cadastro de Pessoas** - Gerenciar membros da residência  
✅ **Cadastro de Transações** - Registrar receitas e despesas  
✅ **Validação de Menores** - Menores de idade só podem registrar despesas  
✅ **Relatório de Totais** - Visualizar saldos consolidados  
✅ **Persistência de Dados** - Dados salvos automaticamente em SQLite  
✅ **Interface Responsiva** - Funciona em desktop e mobile  
✅ **Código Bem Documentado** - Comentários detalhados em todo o código  

## 🏗️ Stack Tecnológico

- **Backend**: ASP.NET Core 8.0 com C#
- **Frontend**: React 18 com TypeScript
- **Banco de Dados**: SQLite
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Estilos**: CSS puro (responsivo)

## 🚀 Como Executar

### 1. Clonar ou Baixar o Projeto

```bash
# Extrair os arquivos do projeto
```

### 2. Executar o Backend

```bash
# Navegar para a pasta do backend
cd ControladorGastos

# Restaurar dependências
dotnet restore

# Executar a aplicação (porta 5000)
dotnet run
```

**API disponível em**: `http://localhost:5000/swagger`

### 3. Executar o Frontend

```bash
# Abrir novo terminal
# Navegar para a pasta do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento (porta 3000)
npm run dev
```

**Aplicação disponível em**: `http://localhost:3000`

## 📖 Como Usar

### 1. Aba Pessoas 👥
- Crie novas pessoas com nome e idade
- Visualize todas as pessoas cadastradas
- Delete uma pessoa (isso também deleta todas suas transações)

### 2. Aba Transações 📊
- Registre receitas e despesas
- **Validação**: Menores de 18 anos só podem registrar despesas
- Visualize todas as transações com nome de quem efetuou

### 3. Aba Relatório de Totais 📈
- Visualize o resumo financeiro por pessoa
- Veja os totais gerais do sistema
- Acompanhe receitas, despesas e saldos

## 📋 Regras de Negócio

### Restrição de Menores de Idade (CRÍTICA)

**Pessoas menores de 18 anos SÓ podem registrar DESPESAS**

- Receitas são bloqueadas para menores
- Mensagem de erro clara ao tentar registrar
- Validação em frontend e backend

### Cascata de Deleção

Ao deletar uma pessoa, TODAS suas transações também serão deletadas automaticamente.

### Persistência de Dados

Todos os dados são salvos em um arquivo SQLite (`controlador-gastos.db`) que persiste após fechar a aplicação.

## 📁 Estrutura do Projeto

```
.
├── ControladorGastos/              # Backend ASP.NET Core
│   ├── Controllers/                # Rotas HTTP
│   ├── Services/                   # Lógica de negócio
│   ├── Models/                     # Entidades
│   ├── Data/                       # DbContext
│   ├── DTOs/                       # Transfer Objects
│   └── Program.cs                  # Configuração
│
├── frontend/                       # Frontend React
│   ├── src/
│   │   ├── components/             # Componentes React
│   │   ├── services/               # Cliente HTTP
│   │   ├── types/                  # Tipos TypeScript
│   │   ├── styles/                 # CSS
│   │   └── App.tsx                 # Componente raiz
│   ├── index.html                  # HTML
│   ├── vite.config.ts              # Config Vite
│   └── package.json                # Dependências npm
│
├── DOCUMENTACAO.md                 # Documentação detalhada
└── README.md                       # Este arquivo
```

## 🔍 Exemplos de Uso

### Criar Pessoa
```
Nome: João Silva
Idade: 30 anos
```

### Criar Transação
```
Pessoa: João Silva (30 anos)
Tipo: Receita
Descrição: Salário
Valor: R$ 3.000,00
```

### Relatório de Totais
```
João Silva (30 anos)
├─ Receitas: R$ 3.000,00
├─ Despesas: R$ 2.500,00
└─ Saldo: R$ 500,00

TOTAIS GERAIS
├─ Total Receitas: R$ 3.000,00
├─ Total Despesas: R$ 2.500,00
└─ Saldo Líquido: R$ 500,00
```

## ✅ Requisitos Atendidos

- ✅ Cadastros de transações com criar e listar
- ✅ Cadastro de pessoas com criar, deletar e listar
- ✅ Consulta de totais com valores consolidados
- ✅ Validação de menores de idade
- ✅ Persistência de dados após fechar aplicação
- ✅ Código bem documentado com comentários
- ✅ Arquitetura clara e padrões de desenvolvimento
- ✅ Interface intuitiva e responsiva
- ✅ Cascata de deleção funcionando corretamente

## 🛠️ Tecnologias Utilizadas

### Backend
- ASP.NET Core 8.0
- Entity Framework Core
- SQLite
- Swagger/OpenAPI
- CORS

### Frontend
- React 18
- TypeScript
- Axios
- Vite
- CSS3 (Grid, Flexbox)

## 📝 Padrões Implementados

- ✅ **MVC Pattern**: Separação de concerns
- ✅ **Service Layer**: Lógica de negócio centralizada
- ✅ **DTOs**: Transfer Objects para camadas
- ✅ **Dependency Injection**: Injeção de dependências
- ✅ **Async/Await**: Operações assíncronas
- ✅ **Error Handling**: Tratamento robusto de erros
- ✅ **Type Safety**: TypeScript para segurança de tipos
- ✅ **Components**: Componentes reutilizáveis

## 🚨 Validações Implementadas

### Backend (C#)
- ✅ Validação de nome (obrigatório, max 200 caracteres)
- ✅ Validação de idade (0-150 anos)
- ✅ Validação de descrição (obrigatória)
- ✅ Validação de valor (maior que zero)
- ✅ Verificação de existência de pessoa
- ✅ Restrição de menores de idade para receitas
- ✅ Existência de chave estrangeira

### Frontend (React)
- ✅ Validação de formulários
- ✅ Mensagens de erro amigáveis
- ✅ Confirmação de deleção
- ✅ Aviso sobre cascata de deleção
- ✅ Desabilitação de opções não permitidas

## 📞 Troubleshooting

**Erro de conexão entre frontend e backend**
- Verificar se backend está rodando em `localhost:5000`
- Verificar se frontend está tentando conectar em `http://localhost:5000`
- Verificar CORS em `Program.cs`

**Banco de dados não funciona**
- Deletar arquivo `controlador-gastos.db`
- Reiniciar a aplicação
- Banco será recriado automaticamente

**Npm install falha**
- Deletar `node_modules` e `package-lock.json`
- Executar `npm install` novamente

## 📚 Documentação Adicional

Veja o arquivo `DOCUMENTACAO.md` para:
- Arquitetura detalhada
- Endpoints da API
- Fluxos de dados
- Exemplos de requisições
- Notas de desenvolvimento

## 📄 Licença

Desenvolvido como teste técnico.

---

**Desenvolvido com ❤️**  
💻 Backend: ASP.NET Core | Frontend: React | DB: SQLite
