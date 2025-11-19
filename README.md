docker compose down --volumes --remove-orphans --rmi all



# SoFiA - Soluções Financeiras

SoFiA é uma plataforma local para gestão financeira pessoal. Permite que usuários rastreiem, categorizem e analisem suas transações financeiras de forma intuitiva e eficiente através de um chat.

## O Que É SoFiA?

SoFiA funciona como seu assistente financeiro pessoal. A aplicação oferece:

- Registro centralizado de todas as transações financeiras
- Organização automática em categorias
- Visualização clara de onde seu dinheiro está indo
- Análise de padrões de gastos
- Interface amigável e responsiva

## Como Funciona?

SoFiA é estruturado em duas partes principais:

### Frontend (React + TypeScript)
Interface web moderna e responsiva onde você gerencia suas finanças. Acesso em http://localhost:5173

### Backend (FastAPI + Python)
API robusta que processa dados, valida informações e mantém tudo sincronizado. Acesso em http://localhost:8000

### Banco de Dados (SQLite)
Armazena seguramente todas as suas transações e categorias localmente.

## Pré-requisitos

Antes de começar, instale:

- **Node.js 18+** (https://nodejs.org/)
- **Python 3.12+** (https://www.python.org/)
- **pnpm** - Gerenciador de pacotes otimizado
- **Poetry** - Gerenciador de dependências Python

## Instalação

### 1. Instalar Ferramentas Globais

```bash
npm install -g pnpm
pnpm add turbo --global
```

Instale Poetry em: https://python-poetry.org/docs/#installation

### 2. Clonar e Preparar

```bash
git clone <url-do-repositorio>
cd SoFiA
pnpm install
```

### 3. Inicializar Banco de Dados

```bash
cd apps/backend
poetry run python scripts/create_db.py
```

## Executar a Aplicação

### Opção 1: Rodar Tudo Junto (Recomendado)

```bash
pnpm turbo dev
```

Isso inicia simultaneamente:
- Frontend em http://localhost:5173
- Backend em http://localhost:8000
- Documentação da API em http://localhost:8000/docs

### Opção 2: Rodar Separadamente

**Frontend:**
```bash
cd apps/frontend
pnpm dev
```

**Backend:**
```bash
cd apps/backend
pnpm dev
```

## Estrutura do Projeto

```
SoFiA/
├── apps/
│   ├── frontend/
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   │
│   └── backend/
│       ├── src/
│       ├── scripts/
│       ├── data/
│       └── pyproject.toml
│
├── packages/
│   └── eslint-config-custom/
│
├── turbo.json
├── pnpm-lock.yaml
└── package.json
```

## Tecnologias Utilizadas

| Componente | Tecnologia |
|-----------|-----------|
| Frontend | React 18, TypeScript, Vite |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite |
| Build | Turborepo, pnpm |

## Recursos Principais

- Dashboard intuitivo de transações
- Gestão flexível de categorias
- Validação automática de dados
- API RESTful bem documentada
- Banco de dados local e seguro
