# YouTubeToolsAgent
A chat agent for summarizing YouTube videos

---

# Architecture & Folder Structure

This project follows **Clean Architecture** / **Domain-Driven Design** principles with clear separation of concerns.

## Folder Purpose Guide

### `domain/` - Pure Business Logic (Core)
**Contains:** Business rules, orchestration, data structures
**Dependencies:** NONE - This is the innermost layer
**Rule:** Code here should work with ANY database or web framework

#### `domain/models/`
Data structures that represent domain concepts
- **Put here:** Dataclasses, value objects (e.g., `AgentResult`, `AgentEvent`)
- **Don't put here:** ORM models, API request/response schemas

#### `domain/services/`
Business orchestration and use case coordination
- **Put here:** Services that orchestrate domain logic (e.g., `WorkspaceService`)
- **Responsibility:** Load data → execute business logic → save results
- **Don't put here:** Database queries, HTTP handling, external API calls

#### `domain/repositories/`
Interfaces for data access (implementation in infrastructure)
- **Put here:** Repository classes that abstract database operations
- **Responsibility:** Define HOW to access data, not WHERE it comes from
- **Pattern:** Accept database session, return domain objects (dicts/dataclasses)

---

### `infrastructure/` - External System Adapters
**Contains:** Database connections, external API clients
**Dependencies:** Depends on `domain/`
**Rule:** Code that connects to external systems

#### `infrastructure/orm_database.py`
Database connection and session management
- **Contains:** SQLAlchemy engine, session factory
- **Exports:** `get_session()`, `engine`
- **Don't put here:** Business logic, ORM models (those go in `api/models/` currently)

---

### `api/` - HTTP Interface Layer
**Contains:** Web framework code (FastAPI)
**Dependencies:** Depends on `domain/`
**Rule:** Code that handles HTTP requests/responses

#### `api/routes/`
HTTP endpoint handlers
- **Put here:** Route definitions, HTTP logic only
- **Responsibility:** Parse requests → call services → return responses
- **Pattern:** Thin controllers - delegate to domain services
- **Don't put here:** Business logic, database queries

#### `api/models/`
⚠️ **Currently contains ORM models (technical debt)**
Should contain: Pydantic request/response schemas
Will be reorganized in future refactor

#### `api/main.py`
FastAPI application setup
- **Contains:** App initialization, middleware, lifecycle events
- **Responsibility:** Wire everything together

---

### `components/` - Legacy Code (Mixed Concerns)
⚠️ **Being refactored** - Contains mix of domain, infrastructure, and business logic

#### `components/agents/`
Agent orchestration logic (should move to `domain/`)

#### `components/anthropic/`
Claude API integration (should move to `infrastructure/`)

#### `components/services/`
Mix of domain services and infrastructure

---

## Dependency Rules

**The Golden Rule:** Dependencies point INWARD

```
┌─────────────────────────────────────┐
│  api/          infrastructure/      │  ← Outer layers
│    ↓                ↓                │
│         domain/                      │  ← Inner layer (pure)
└─────────────────────────────────────┘
```

- ✅ `api/` can import from `domain/`
- ✅ `infrastructure/` can import from `domain/`
- ❌ `domain/` NEVER imports from `api/` or `infrastructure/`

---

## Decision Tree: Where Does This File Go?

```
Does it handle HTTP requests/responses?
  YES → api/routes/
  NO ↓

Does it connect to external systems (DB, APIs, filesystem)?
  YES → infrastructure/
  NO ↓

Is it pure business logic or data structure?
  YES → domain/
    ├─ Data structure? → domain/models/
    ├─ Orchestration? → domain/services/
    └─ Data access? → domain/repositories/
```

---

## Current Refactor Status

**Slice 1 (In Progress):** Message persistence with service layer
- ✅ Created `domain/models/agent_result.py`
- ✅ Modified `components/agents/chat_agent.py` to return `AgentResult`
- 🔄 Creating `domain/repositories/message_repository.py`
- 🔄 Creating `domain/services/workspace_service.py`
- ⏳ Refactoring `api/routes/messages.py` to use service

**Future Work:**
- Move ORM models from `api/models/` to `infrastructure/models/`
- Move Claude client from `components/anthropic/` to `infrastructure/anthropic/`
- Consolidate agent code from `components/agents/` to `domain/`

---

# Setup
1. Create a virtual environment `python -m venv venv` the app was built in v3.11.5
1. Activate the virtual env 
     1. *nix: `source venv/bin/activate`
     2. Windows: `venv\Scripts\activate`
1. Install dependencies: `pip install -r requirements.txt`
1. create an `.env` file in the project root with the following content
```commandline
YOUTUBE_API_KEY=<YOUTUBE API KEY>
ANTHROPIC_API_KEY=<ANTHROPIC API KEY>
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@localhost:5432/content_analysis
```
<!--
claude keys are available here: https://console.anthropic.com/settings/keys
youtube keys are available here: https://console.cloud.google.com/apis/credentials?pli=1&project=resfracweather
-->
1. Install Python Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```
1. Setup Postgres Database
1. Create the database:
```bash
psql -h localhost -U postgres -c "CREATE DATABASE content_analysis;"
```

1. Apply Database Schema

Create all database tables:
```bash
# First time setup (fresh start)
python database/apply_schema.py --fresh

# Subsequent runs (preserves data)
python database/apply_schema.py
```

# Application 2

## Start the app
activate the virtual env first
```
> ./MainChat.py
```

## Use the app

> \> I want you to watch two videos and tell me which one is better to learn about the current state of AI.  Here are the videos: https://www.youtube.com/watch?v=L32th5fXPw8 https://www.youtube.com/watch?v=obqjIoKaqdM&t=7s <br>
 \> ok that's not what I'm looking for.  Try this next one https://www.youtube.com/watch?v=DdlMoRSojtE https://www.youtube.com/watch?v=esqPTMDvw7w https://www.youtube.com/watch?v=264QcC094Vk


# Application 1 [Currently Broken]
The command line app is a command driven CLI. Users type explicit commands.

## Start the app
activate the virtual env first
```
> ./MainCli.py
```
## Use the app
````commandline
> help
> watch_video https://www.youtube.com/watch?v=obqjIoKaqdM
> list_videos
> summarize_video 0
> ask_question who is the creator, what channel is this?
````

## TODO 
* expose the prompts in a config file so they can more easily be edited
* select Claude model from a single config
* use the Claude stream interface to provide more frequent responses to the user, instead of all at once
* ChatSession is not symmetric.  ChatMessages are input, but anthropic messages are returned.