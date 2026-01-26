# Bedrock Chat - Agent Guidelines

This document provides instructions for AI coding agents working in this repository.

## Project Overview

Bedrock Chat is a multilingual generative AI platform powered by Amazon Bedrock. It's a monorepo with three main components:

- `backend/` - Python FastAPI backend (Python 3.13+)
- `frontend/` - React TypeScript frontend (React 18, TypeScript 5)
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

# Run all tests
npm test

# Run a single test file
npm test -- src/utils/__tests__/MessageUtils.test.ts

# Run tests matching a pattern
npm test -- --grep "convertMessageMapToArray"

# Lint code
npm run lint

# Format code (via pre-commit hook or manually)
npx prettier --write "src/**/*.{ts,tsx}"
```

### CDK (Infrastructure)

```bash
cd cdk

# Install dependencies
npm ci

# Build TypeScript
npm run build

# Run tests
npm test

# Run a single test
npm test -- --testPathPattern="parameter-models"

# Deploy (requires AWS credentials)
npx cdk deploy --all
```

## Code Style Guidelines

### Frontend (TypeScript/React)

**Formatting (Prettier):**
- 2-space indentation
- Single quotes
- Semicolons required
- Trailing commas (ES5)
- Arrow function parentheses always

**Naming Conventions:**
- Components: `PascalCase` (e.g., `BotKbEditPage.tsx`)
- Hooks: `camelCase` with `use` prefix (e.g., `useChat.ts`)
- Functions/variables: `camelCase` (e.g., `onClickCreate`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_GENERATION_CONFIG`)
- Types/Interfaces: `PascalCase` (e.g., `MessageContent`, `BotInputType`)

**Import Order:**
1. React imports
2. Third-party libraries
3. Local imports (components, hooks, utils)

**Patterns:**
- Functional components with TypeScript (no class components)
- Use `useCallback` and `useMemo` for performance optimization
- Zustand for global state management
- Immer (`produce`) for immutable state updates
- SWR for data fetching with automatic caching
- Early returns to reduce nesting

**ESLint Rules:**
- Curly braces required for all blocks
- Unused variables prefixed with `_` are allowed
- React hooks rules enforced

### Backend (Python)

**Formatting:**
- Black formatter (default settings)
- PEP 8 style guide

**Type Hints:**
- Required for all function parameters and return values
- Use Pydantic models for data validation
- mypy for static type checking (ignores test files)

**Naming Conventions:**
- Functions/variables: `snake_case` (e.g., `prepare_conversation`)
- Classes: `PascalCase` (e.g., `BotModel`, `ConversationModel`)
- Constants: `UPPER_SNAKE_CASE`
- Private methods: prefix with `_` (e.g., `_create_model`)
- Modules: `snake_case` (e.g., `custom_bot.py`)

**Architecture Patterns:**
- Layered: Routes (API) -> UseCases (business logic) -> Repositories (data access)
- Pydantic models with `@field_validator` and `@model_validator` for validation
- Factory methods (`from_input`, `from_dynamo_item`) for model creation
- Conversion methods (`to_output`, `to_summary_output`) for API responses

**Testing:**
- pytest framework
- Test files: `test_*.py` in `tests/` directory
- Use `unittest.TestCase` for test classes
- `setUp` and `tearDown` for test fixtures

### CDK (Infrastructure)

- TypeScript with strict mode
- Jest for testing
- Constructs for reusable components

## Pre-commit Hooks (Lefthook)

The repository uses Lefthook for pre-commit hooks:

**Backend:** `black` (format) + `mypy` (type check)
**Frontend:** `prettier` (format) + `eslint` (lint)

Run manually if needed:
```bash
# Backend
cd backend && poetry run black app && poetry run mypy --config-file mypy.ini app

# Frontend  
cd frontend && npx prettier --write "src/**/*.{ts,tsx}" && npx eslint --fix "src/**/*.{ts,tsx}"
```

## Error Handling

**Frontend:**
- Use React Error Boundary for component errors
- SWR handles API error states automatically
- Form validation with centralized `isValid()` functions

**Backend:**
- Pydantic validators raise `ValueError` for invalid data
- `RecordNotFoundError` for missing database records
- Use `tenacity` for retries on transient failures

## Key Dependencies

**Backend:** FastAPI, Pydantic, Boto3, strands-agents, opensearch-py
**Frontend:** React 18, Zustand, SWR, Tailwind CSS, XState, Immer
**CDK:** aws-cdk-lib, @cdklabs/generative-ai-cdk-constructs

## Workspace Boundaries

All file operations must remain within this repository. Do not access files outside the project workspace.
