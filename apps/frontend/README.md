# SofIA Frontend

Aplicativo de assistente financeiro inteligente construído com React, Vite, TypeScript e TailwindCSS.

## Funcionalidades

- Interface de chat interativo com IA financeira
- Dashboard com visualizações de dados em tempo real
- Gerenciamento de sessões de chat múltiplas
- Configurações de perfil e API key
- Suporte a múltiplos modelos de IA
- Design responsivo e moderno
- Tema claro/escuro

## Começando

1. **Instalar dependências:**
\`\`\`bash
npm install
# ou
pnpm install
\`\`\`

2. **Configurar variáveis de ambiente:**
\`\`\`bash
cp .env.example .env
\`\`\`

Edite `.env` e adicione a URL da sua API backend:
\`\`\`
VITE_API_BASE_URL=http://localhost:8000
\`\`\`

3. **Iniciar servidor de desenvolvimento:**
\`\`\`bash
npm run dev
# ou
pnpm dev
\`\`\`

4. **Abrir [http://localhost:5173](http://localhost:5173)**

## Estrutura do Projeto

\`\`\`
src/
├── components/          # Componentes reutilizáveis
│   ├── ui/             # Componentes shadcn/ui
│   ├── MessageBubble.tsx
│   ├── SuggestionCard.tsx
│   ├── TypingIndicator.tsx
│   └── Layout.tsx
├── features/           # Lógica de funcionalidades
│   └── chat/
│       ├── hooks/      # Custom hooks do React Query
│       ├── services/   # Funções de API
│       └── types/      # Interfaces TypeScript
├── pages/              # Páginas da aplicação (React Router)
│   ├── Chat.tsx
│   ├── Dashboard.tsx
│   ├── Home.tsx
│   ├── Profile.tsx
│   ├── Settings.tsx
│   └── NotFound.tsx
├── stores/             # Stores Zustand (se necessário)
├── hooks/              # Hooks globais
├── lib/                # Utilitários
│   ├── api/           # Cliente API (Axios)
│   ├── env.ts         # Validação de env vars
│   └── utils.ts       # Funções auxiliares
└── App.tsx             # Componente raiz
\`\`\`

## Stack Tecnológica

- **Framework**: React 18 + Vite
- **Roteamento**: React Router v6
- **State Management**: TanStack Query (React Query) + Zustand
- **UI Components**: shadcn/ui + Radix UI
- **Estilização**: Tailwind CSS v4
- **Formulários**: React Hook Form + Zod
- **Charts**: Recharts
- **TypeScript**: Tipagem estrita completa
- **HTTP Client**: Axios

## Integração com Backend

A aplicação se conecta ao backend SofIA através das seguintes rotas:

- `POST /api/v1/users` - Criar novo usuário
- `PUT /api/v1/users` - Atualizar usuário (nome e API key)
- `GET /api/v1/chat/sessions` - Listar todas as sessões de chat
- `POST /api/v1/chat/sessions/:id/messages` - Enviar mensagem
- `PUT /api/v1/chat/sessions/:id` - Atualizar título da sessão
- `DELETE /api/v1/chat/sessions/:id` - Deletar sessão

Veja `src/features/chat/types/index.ts` para definições completas de tipos.

## Padrões de Código

- **Componentes funcionais** com React Hooks
- **TypeScript estrito** sem uso de `any`
- **Separação de responsabilidades**: lógica em hooks, UI em componentes
- **State management**: 
  - TanStack Query para estado do servidor (API data)
  - Zustand para estado global do cliente (se necessário)
- **Validação**: Zod schemas para forms e env vars
- **Convenção de nomes**: PT-BR para textos de interface

## Scripts Disponíveis

\`\`\`bash
npm run dev          # Inicia servidor de desenvolvimento (porta 5173)
npm run build        # Build de produção
npm run preview      # Preview do build de produção
npm run lint         # Executa ESLint
\`\`\`

## Estrutura de Dados

### Transação
\`\`\`typescript
{
  id: number
  amount: number
  description: string
  transaction_type: 'income' | 'expense'
  category_id?: number
  is_superfluous?: boolean
  user_id: number
  created_at: string
}
\`\`\`

### Sessão de Chat
\`\`\`typescript
{
  id: number
  user_id: number
  title?: string
  pending_tool?: string
  collected_params: object
  missing_fields: string[]
  created_at: string
}
\`\`\`

### Mensagem de Chat
\`\`\`typescript
{
  id: number
  session_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  meta_data?: object
  created_at: string
}
\`\`\`

## Gerenciamento de Estado

### TanStack Query (Server State)
- Caching automático de dados da API
- Refetch em background
- Otimistic updates
- Invalidação inteligente de cache

### Axios Interceptors
- Tratamento global de erros
- Toast notifications automáticas
- Timeout configurável (30s)

## Próximos Passos

- [ ] Implementar autenticação completa
- [ ] Adicionar testes unitários e E2E
- [ ] Implementar tema dark mode toggle
- [ ] Adicionar mais visualizações no Dashboard
- [ ] Implementar exportação de dados financeiros
- [ ] PWA support
\`\`\`
