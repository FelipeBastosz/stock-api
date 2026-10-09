# Stock Management API — 愚公移山 Variedades

API RESTful para controle de estoque, catálogo de produtos, fornecedores e auditoria de movimentações.

## Tecnologias

- Python 3.12+
- FastAPI
- PostgreSQL + asyncpg
- SQLAlchemy 2.0 (Async)
- Alembic
- Loguru
- Docker & Docker Compose

## Estrutura do Projeto

```text
estoque-api/
├── alembic/                  # Migrações do banco de dados
├── src/
│   ├── core/                 # Configurações, banco de dados, logging e erros
│   ├── modules/              # Módulos da aplicação (categorias, fornecedores, produtos, etc.)
│   └── main.py               # Ponto de entrada da aplicação
├── docker-compose.yml        # PostgreSQL
├── requirements.txt
└── .env.example
```

## Como Executar

### 1. Ambiente Virtual e Dependências

```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Variáveis de Ambiente

```bash
cp .env.example .env
```

### 3. Banco de Dados

```bash
docker compose up -d
```

### 4. Executar a API

```bash
uvicorn src.main:app --reload --port 8000
```

- Documentação Swagger: `http://localhost:8000/docs`
- Documentação ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`