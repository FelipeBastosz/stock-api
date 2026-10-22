# Stock Management API

API RESTful de alta performance para controle de estoque, catálogo de produtos, gestão de fornecedores e auditoria imutável de movimentações.

Projetada com arquitetura assíncrona, transações atômicas de saldo com bloqueio pessimista contra condições de corrida (*race conditions*), autenticação JWT com papéis de acesso (RBAC), suíte de testes automatizados e esteira de CI no GitHub Actions.

---

## 🚀 Tecnologias

* **Linguagem**: Python 3.12+
* **Framework Web**: FastAPI (com Pydantic v2 e validação em tempo de execução)
* **Banco de Dados**: PostgreSQL + driver assíncrono `asyncpg`
* **ORM & Migrações**: SQLAlchemy 2.0 (Async) + Alembic
* **Segurança**: PyJWT (tokens JWT) + Bcrypt (hashing seguro de senhas)
* **Logging Estruturado**: Loguru com interceptação de logs de framework
* **Testes Automatizados**: Pytest + pytest-asyncio + HTTPX + aiosqlite
* **DevOps & CI**: Docker Compose + GitHub Actions CI Workflow

---

## 🏛️ Arquitetura do Projeto

```text
estoque-api/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de testes e validação automática no GitHub Actions
├── alembic/
│   ├── versions/                # Migrações versionadas do banco de dados
│   └── env.py                   # Configuração assíncrona do Alembic
├── docs/
│   └── postman_collection.json  # Collection exportada para Postman / Insomnia
├── src/
│   ├── core/                    # Módulos transversais da aplicação
│   │   ├── config.py            # Variáveis de ambiente tipadas (pydantic-settings)
│   │   ├── database.py          # Conexão assíncrona PostgreSQL e sessão
│   │   ├── exceptions.py        # Hierarquia semântica de exceções customizadas
│   │   ├── handlers.py          # Handlers globais de erro (sem vazamento de stack trace)
│   │   ├── logging.py           # Logging estruturado com Loguru
│   │   └── security.py          # Hashing de senhas (bcrypt) e tokens JWT
│   ├── modules/                 # Módulos de domínio de negócio
│   │   ├── auth/                # Autenticação, usuários e controle de perfil (RBAC)
│   │   ├── categories/          # Gestão de categorias e validação de vínculos
│   │   ├── suppliers/           # Fornecedores com unicidade de CNPJ/Email
│   │   ├── products/            # Catálogo de produtos, filtros e relatório de estoque crítico
│   │   └── movements/           # Movimentações imutáveis com lock pessimista
│   └── main.py                  # Ponto de entrada, middlewares e registro de rotas
├── tests/                       # Suíte de testes automatizados com SQLite em memória
├── docker-compose.yml           # Contêiner PostgreSQL
├── pytest.ini                   # Configurações de execução do pytest
├── requirements.txt             # Dependências do projeto
└── .env.example                 # Modelo de configuração de variáveis de ambiente
```

---

## 🌟 Principais Recursos e Diferenciais de Engenharia

1. **Prevenção de Race Conditions (Lock Pessimista)**:
   Ao registrar saídas de estoque concorrentes, a busca do produto utiliza `SELECT ... FOR UPDATE` (`with_for_update()`). Isso impede que requisições simultâneas ignorem o saldo real ou deixem o estoque negativo.
2. **Imutabilidade e Auditoria Contábil**:
   As movimentações de estoque são estritamente de *append-only* (apenas `POST` e `GET`). Não há endpoints de `PUT` ou `DELETE`, preservando a rastreabilidade fiscal e contábil.
3. **Integridade Referencial com Bloqueio de Exclusão**:
   * Categorias com produtos vinculados retornam HTTP 400 (`BusinessRuleException`).
   * Fornecedores com produtos vinculados retornam HTTP 400 (`BusinessRuleException`).
   * Produtos com histórico de movimentações retornam HTTP 400 (`BusinessRuleException`).
4. **Tratamento Seguro de Exceções**:
   Todas as respostas de erro seguem um padrão uniforme (`status_code`, `error`, `message`, `details`). Erros internos inesperados (HTTP 500) têm seu stack trace logado internamente sem expor detalhes sensíveis ao cliente.
5. **Autenticação e RBAC (Role-Based Access Control)**:
   Emissão de tokens JWT com suporte a perfis `admin` (gestão completa do catálogo) e `operator` (consulta e registro de entradas/saídas).
6. **Relatórios Estratégicos**:
   * `GET /products/low-stock`: lista produtos com estoque no mínimo ou abaixo, ordenados pela gravidade do déficit.
   * `GET /movements/summary`: resumo analítico consolidado de entradas, saídas e saldo líquido do período.

---

## 🛠️ Como Executar o Projeto

### 1. Clonar o Repositório e Criar o Ambiente Virtual

```bash
git clone https://github.com/FelipeBastosz/stock-api.git
cd stock-api

# Criar e ativar o ambiente virtual:
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate

# Instalar dependências:
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

### 3. Iniciar o Banco de Dados com Docker

```bash
docker compose up -d
```

### 4. Executar as Migrações do Banco

```bash
alembic upgrade head
```

### 5. Iniciar a API

```bash
uvicorn src.main:app --reload --port 8000
```

* **Swagger Interativo**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Documentação ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Suíte de Testes Automatizados

A suíte de testes utiliza um banco SQLite assíncrono em memória (`aiosqlite`) totalmente isolado, executando todos os testes de integração e regras de negócio em ~1 segundo:

```bash
pytest -v
```

A integridade do código também é validada automaticamente a cada push ou pull request através do GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

---

## 📑 Resumo dos Endpoints e Permissões (RBAC)

| Método | Endpoint | Descrição | Permissão |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Verificação de integridade e versão da API | Público |
| `POST` | `/auth/register` | Cadastro de usuário (`admin` ou `operator`) | Público |
| `POST` | `/auth/login` | Login com formulário OAuth2 (Swagger) | Público |
| `POST` | `/auth/token` | Login via JSON retornando JWT | Público |
| `GET` | `/auth/me` | Dados do usuário autenticado | Autenticado |
| `POST` | `/categories` | Criar nova categoria (nome único) | **Admin** |
| `GET` | `/categories` | Listar categorias com paginação | Público |
| `GET` | `/categories/{id}` | Obter detalhes da categoria | Público |
| `PUT` | `/categories/{id}` | Atualizar categoria | **Admin** |
| `DELETE` | `/categories/{id}` | Excluir categoria (bloqueia se houver produtos) | **Admin** |
| `POST` | `/suppliers` | Criar fornecedor (CNPJ e Email únicos) | **Admin** |
| `GET` | `/suppliers` | Listar fornecedores com paginação | Público |
| `GET` | `/suppliers/{id}` | Obter detalhes do fornecedor | Público |
| `PUT` | `/suppliers/{id}` | Atualizar fornecedor | **Admin** |
| `DELETE` | `/suppliers/{id}` | Excluir fornecedor (bloqueia se houver produtos) | **Admin** |
| `POST` | `/products` | Cadastrar produto no catálogo | **Admin** |
| `GET` | `/products` | Listar produtos com filtros (`busca`, `categoria_id`, etc.) | Público |
| `GET` | `/products/low-stock` | **Relatório estratégico de estoque crítico** | Público |
| `GET` | `/products/{id}` | Detalhes do produto com categoria e fornecedor | Público |
| `PUT` | `/products/{id}` | Atualizar produto | **Admin** |
| `DELETE` | `/products/{id}` | Excluir produto (bloqueia se houver movimentações) | **Admin** |
| `POST` | `/movements` | **Registrar entrada ou saída com lock pessimista** | **Admin / Operador** |
| `GET` | `/movements` | Histórico com filtros (`data_inicio`, `fornecedor_id`, etc.) | **Admin / Operador** |
| `GET` | `/movements/summary` | **Relatório analítico consolidado do período** | **Admin / Operador** |
| `GET` | `/movements/{id}` | Detalhes de uma movimentação por ID | **Admin / Operador** |

> **Nota de Integração**: A API possui suporte a **CORS (Cross-Origin Resource Sharing)** pré-configurado, permitindo integração direta com aplicações web (React, Vue, Vite) e mobile sem bloqueios de origem cruzada.

---

## 📚 Materiais Complementares

* **Collection Postman / Insomnia**: Disponível em [`docs/postman_collection.json`](docs/postman_collection.json) com todos os payloads e testes pré-configurados.