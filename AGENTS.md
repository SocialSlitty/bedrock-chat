# Bedrock Chat - Agent Guidelines

Instructions for AI coding agents working in this repository.

## Project Overview

Bedrock Chat is a multilingual generative AI platform powered by Amazon Bedrock. Monorepo structure:

- `backend/` - Python FastAPI backend (Python 3.13+)
- `frontend/` - React TypeScript frontend (React 18, TypeScript 5, Vite)
- `cdk/` - AWS CDK infrastructure (TypeScript, CDK 2.x)

## Build, Lint, and Test Commands

### Backend (Python)

```bash
cd backend

# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_usecases/test_bot.py

# Run a single test function
poetry run pytest tests/test_usecases/test_bot.py::TestModifyBotVisibility::test_modify_visibility_to_private

# Type checking
poetry run mypy app

# Format code
poetry run black app
```

### Frontend (TypeScript/React)

```bash
cd frontend

# Install dependencies
npm ci

# Run development server
npm run dev

# Build for production
npm run build

# Run all tests (Vitest)
npm test

# Run a single test file
npm test -- src/utils/__tests__/MessageUtils.test.ts

# Run tests matching a pattern
npm test -- --grep "convertMessageMapToArray"

# Lint code
npm run lint

# Format code
npx prettier --write "src/**/*.{ts,tsx}"
```

### CDK (Infrastructure)

```bash
cd cdk

# Install dependencies
npm ci

# Build TypeScript
npm run build

# Run tests (Jest)
npm test

# Run a single test
npm test -- --testPathPattern="parameter-models"

# Deploy (requires AWS credentials)
npx cdk deploy --all
```

## Code Style Guidelines

### Frontend (TypeScript/React)

**Prettier Config** (`.prettierrc.json`):
- 2-space indentation, single quotes, semicolons required
- Trailing commas (ES5), arrow parens always
- Uses `prettier-plugin-tailwindcss`

**ESLint Rules**:
- Curly braces required for all blocks (`curly: ['error', 'all']`)
- Unused variables: prefix with `_` to allow (`varsIgnorePattern: "^_"`)
- React hooks rules enforced

**Naming Conventions**:
- Components: `PascalCase` (e.g., `BotKbEditPage.tsx`)
- Hooks: `camelCase` with `use` prefix (e.g., `useChat.ts`)
- Functions/variables: `camelCase` (e.g., `onClickCreate`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_GENERATION_CONFIG`)
- Types/Interfaces: `PascalCase` (e.g., `MessageContent`, `BotInputType`)

**Import Order**: React imports → Third-party libraries → Local imports

**Patterns**:
- Functional components with TypeScript (no class components)
- Zustand for global state, Immer for immutable updates
- SWR for data fetching with automatic caching
- XState for complex state machines
- `useCallback` and `useMemo` for performance optimization
- Early returns to reduce nesting

### Backend (Python)

**Formatting**: Black formatter (default settings), PEP 8 style

**Type Hints** (required):
- All function parameters and return values must have type hints
- Pydantic models for data validation
- mypy for static type checking (ignores test files per `mypy.ini`)

**Naming Conventions**:
- Functions/variables: `snake_case` (e.g., `prepare_conversation`)
- Classes: `PascalCase` (e.g., `BotModel`, `ConversationModel`)
- Constants: `UPPER_SNAKE_CASE`
- Private methods: prefix with `_` (e.g., `_create_model`)
- Modules: `snake_case` (e.g., `custom_bot.py`)

**Architecture** (layered):
- Routes (`app/routes/`) - API endpoints
- UseCases (`app/usecases/`) - Business logic
- Repositories (`app/repositories/`) - Data access

**Pydantic Patterns**:
- `@field_validator` and `@model_validator` for validation
- Factory methods: `from_input()`, `from_dynamo_item()`
- Output methods: `to_output()`, `to_summary_output()`

**Testing**:
- pytest framework with `unittest.TestCase` classes
- Test files: `test_*.py` in `tests/` directory
- Use `setUp()` and `tearDown()` for fixtures

### CDK (Infrastructure)

**Prettier Config** (`.prettierrc`): 2-space indent, double quotes, semicolons

**Patterns**: TypeScript strict mode, Jest for testing, reusable Constructs

## Pre-commit Hooks (Lefthook)

Runs automatically on commit:
- **Backend**: `black` (format) + `mypy` (type check)
- **Frontend**: `prettier` (format) + `eslint` (lint)

Run manually:
```bash
# Backend
cd backend && poetry run black app && poetry run mypy --config-file mypy.ini app

# Frontend
cd frontend && npx prettier --write "src/**/*.{ts,tsx}" && npx eslint --fix "src/**/*.{ts,tsx}"
```

## Error Handling

**Frontend**: React Error Boundary, SWR error states, centralized `isValid()` validation

**Backend**: Pydantic validators raise `ValueError`, `RecordNotFoundError` for missing records, `tenacity` for retries

## Key Dependencies

| Component | Main Dependencies |
|-----------|-------------------|
| Backend   | FastAPI, Pydantic, Boto3, strands-agents, opensearch-py |
| Frontend  | React 18, Zustand, SWR, Tailwind CSS, XState, Immer, Vitest |
| CDK       | aws-cdk-lib, @cdklabs/generative-ai-cdk-constructs |

## Workspace Boundaries

All file operations must remain within this repository. Do not access files outside the project workspace.
