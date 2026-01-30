# AGENTS.md - Bedrock Chat

> Guidelines for AI agents working in this AWS Bedrock-powered multilingual chat platform.

## Project Overview

Monorepo with three main components:

| Component | Stack | Location |
|-----------|-------|----------|
| Backend | Python 3.13+, FastAPI, Pydantic, strands-agents | `backend/` |
| Frontend | React 18, TypeScript 5, Vite, Tailwind CSS | `frontend/` |
| CDK | AWS CDK 2.x, TypeScript | `cdk/` |

## Build, Lint, Test Commands

### Backend (Python)

```bash
cd backend

# Install
poetry install

# Dev server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tests
poetry run pytest                                    # All tests
poetry run pytest tests/test_usecases/test_bot.py   # Single file
poetry run pytest tests/test_usecases/test_bot.py::TestModifyBotVisibility::test_modify_visibility_to_private  # Single test

# Type check & format
poetry run mypy app
poetry run black app
```

### Frontend (TypeScript/React)

```bash
cd frontend

# Install
npm ci

# Dev server
npm run dev

# Build
npm run build

# Tests (Vitest)
npm test                                            # All tests
npm test -- src/utils/__tests__/MessageUtils.test.ts  # Single file
npm test -- --grep "convertMessageMapToArray"       # Pattern match

# Lint & format
npm run lint
npx prettier --write "src/**/*.{ts,tsx}"
```

### CDK (Infrastructure)

```bash
cd cdk

# Install & build
npm ci && npm run build

# Tests (Jest)
npm test                                           # All tests
npm test -- --testPathPattern="parameter-models"   # Single test

# Deploy
npx cdk deploy --all
```

## Pre-commit Hooks (Lefthook)

Runs automatically on commit:
- **Backend**: `black` + `mypy`
- **Frontend**: `prettier` + `eslint`

Manual run:
```bash
cd backend && poetry run black app && poetry run mypy --config-file mypy.ini app
cd frontend && npx prettier --write "src/**/*.{ts,tsx}" && npx eslint --fix "src/**/*.{ts,tsx}"
```

## Code Style

### Frontend (TypeScript/React)

**Prettier** (`.prettierrc.json`):
- 2-space indent, single quotes, semicolons required
- Trailing commas (ES5), arrow parens always
- `prettier-plugin-tailwindcss` for class sorting

**ESLint**:
- `curly: ['error', 'all']` - braces required for all blocks
- Unused vars: prefix with `_` to ignore (`varsIgnorePattern: "^_"`)
- React hooks rules enforced

**Naming**:
```typescript
// Components: PascalCase
BotKbEditPage.tsx, ChatMessage.tsx

// Hooks: camelCase with use prefix
useChat.ts, useBot.ts

// Functions/variables: camelCase
onClickCreate, isLoading, handleSubmit

// Constants: UPPER_SNAKE_CASE
DEFAULT_GENERATION_CONFIG, MAX_TOKENS

// Types/Interfaces: PascalCase
MessageContent, BotInputType, ConversationMeta
```

**Import Order**:
```typescript
// 1. React imports
import { useState, useCallback } from 'react';

// 2. Third-party libraries
import { useTranslation } from 'react-i18next';
import useSWR from 'swr';

// 3. Local imports
import { useBot } from '../hooks/useBot';
import Button from '../components/Button';
```

**Patterns**:
- Functional components only (no class components)
- Zustand for global state, Immer for immutable updates
- SWR for data fetching with caching
- XState for complex state machines
- `useCallback`/`useMemo` for performance
- Early returns to reduce nesting

### Backend (Python)

**Formatting**: Black (default settings), PEP 8

**Type Hints** (required on all functions):
```python
def prepare_conversation(
    user_id: str,
    bot_id: str,
    conversation_id: str | None = None
) -> ConversationModel:
```

**Naming**:
```python
# Functions/variables: snake_case
prepare_conversation, user_id, is_valid

# Classes: PascalCase
BotModel, ConversationModel, KnowledgeBaseConfig

# Constants: UPPER_SNAKE_CASE
DEFAULT_MODEL, MAX_RETRIES

# Private methods: _prefix
def _create_model(self): ...
```

**Architecture** (layered):
```
app/
├── routes/       # API endpoints (FastAPI routers)
├── usecases/     # Business logic
├── repositories/ # Data access (DynamoDB, OpenSearch)
└── models/       # Pydantic models
```

**Pydantic Patterns**:
```python
class BotModel(BaseModel):
    @field_validator('name')
    def validate_name(cls, v): ...
    
    @classmethod
    def from_dynamo_item(cls, item: dict) -> 'BotModel': ...
    
    def to_output(self) -> BotOutput: ...
```

**Testing**: pytest with `unittest.TestCase` classes, `setUp()`/`tearDown()` fixtures

### CDK (Infrastructure)

- TypeScript strict mode
- 2-space indent, double quotes, semicolons
- Jest for testing
- Reusable Constructs pattern

## Error Handling

**Frontend**:
- React Error Boundary for component errors
- SWR error states for API errors
- Centralized `isValid()` validation helpers

**Backend**:
- Pydantic validators raise `ValueError`
- `RecordNotFoundError` for missing records
- `tenacity` for retry logic

## Key Dependencies

| Component | Core Libraries |
|-----------|----------------|
| Backend | FastAPI, Pydantic, Boto3, strands-agents, opensearch-py, tenacity |
| Frontend | React 18, Zustand, SWR, Tailwind CSS, XState, Immer, Vitest, react-i18next |
| CDK | aws-cdk-lib, @cdklabs/generative-ai-cdk-constructs |

## Workspace Boundaries

**CRITICAL**: All operations must remain within `/Users/christiansmith/Documents/GitHub/bedrock-chat`

- Never access files outside this workspace
- Use relative paths when possible
- Subagents must also respect these boundaries

**Off-limits**: `/Users/christiansmith/Desktop/Hayaku` - do not read/write/list files there

## Do's and Don'ts

### Do
- Follow existing patterns in the file you're modifying
- Run `poetry run black` and `poetry run mypy` before committing backend changes
- Run `npm run lint` and `npx prettier --write` before committing frontend changes
- Use type hints on all Python functions
- Use early returns to reduce nesting
- Handle errors gracefully with appropriate error types

### Don't
- Skip type hints in Python code
- Use class components in React (functional only)
- Suppress TypeScript errors with `@ts-ignore` or `as any`
- Access files outside the workspace boundary
- Commit without running pre-commit hooks
