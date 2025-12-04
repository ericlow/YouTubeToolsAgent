# Technical Requirements Document
## YouTube Research Tool - Console to Backend Service Conversion

**Version**: 1.2
**Date**: December 4, 2025
**Author**: Eric
**Status**: Draft

---

## 1. Executive Summary

### 1.1 Project Goal
Convert the existing YouTube Research Tool from a CLI application to a professional backend service deployed on AWS, implementing enterprise-level practices for security, observability, reliability, and maintainability.

### 1.2 Scope
**Release 1 (MVP Backend)**:
- FastAPI REST API endpoints
- PostgreSQL database persistence (AWS RDS)
- AWS EC2 deployment
- Basic API key authentication
- CloudWatch logging
- CI/CD pipeline with GitHub Actions
- Code quality tooling (type hints, linting)

**Release 2 (Polish & Hardening)**:
- Security hardening (rate limiting, HTTPS)
- Observability (metrics, alerts, dashboards)
- Reliability improvements (health checks, retries, circuit breakers)
- Unit and integration tests
- AWS Cognito authentication

### 1.3 Success Criteria
- All API endpoints functional and accessible via public IP
- Database persistence verified across server restarts
- Stateless backend confirmed with concurrent sessions
- Remote testing successful (submit URL → get summary → ask questions → verify history)
- All responses under 10 seconds

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────┐
│   Next.js   │ (Future - Not in Release 1)
│  Frontend   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────────────────┐
│           AWS EC2 (t2.micro)                │
│  ┌────────────────────────────────────┐    │
│  │        FastAPI Backend              │    │
│  │  - REST API endpoints               │    │
│  │  - Business logic                   │    │
│  │  - Service orchestration            │    │
│  └────┬───────────────────────┬────────┘    │
│       │                       │              │
└───────┼───────────────────────┼──────────────┘
        │                       │
        ▼                       ▼
┌──────────────┐        ┌─────────────────┐
│ External APIs│        │  AWS RDS        │
│              │        │  PostgreSQL 15  │
│ - Claude API │        │  (db.t3.micro)  │
│ - YouTube API│        │                 │
└──────────────┘        └─────────────────┘
```

### 2.2 Component Architecture

```
YouTubeToolsAgent/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, endpoints
│   ├── models.py            # SQLAlchemy ORM models
│   ├── database.py          # DB connection/session management
│   └── middleware.py        # Auth, logging, CORS
├── components/
│   ├── agents/
│   │   └── chat_agent.py    # AI orchestration (reused)
│   ├── anthropic/
│   │   ├── anthropic_service.py  # Claude API wrapper (reused)
│   │   ├── chat_session.py       # Conversation management (reused)
│   │   └── ...
│   ├── services/
│   │   ├── youtube_service.py    # YouTube API + transcripts (reused)
│   │   └── ...
│   └── ...
├── docs/
│   ├── TRD.md               # This document
│   ├── architecture.md      # Architecture diagrams
│   └── deployment.md        # Deployment runbook
├── .github/
│   └── workflows/
│       ├── test.yml         # Run tests on PR
│       └── deploy.yml       # Deploy on merge to main
├── requirements.txt
├── .env.example
└── README.md
```

### 2.3 Data Flow

**Request Flow**:
1. Client sends HTTP request to EC2 public IP
2. FastAPI receives request, validates API key
3. Business logic executed using existing services
4. External APIs called (Claude, YouTube)
5. Results persisted to RDS PostgreSQL
6. JSON response returned to client
7. Request logged to CloudWatch

**Stateless Pattern**:
- No in-memory session storage
- Each request contains session_id
- Backend loads state from DB → processes → saves to DB
- Enables horizontal scaling

---

## 3. Database Design

### 3.1 Schema

```sql
-- Users table (future: populated by Cognito)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table (chat conversations)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Videos table
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    video_id VARCHAR(50) UNIQUE NOT NULL,  -- YouTube video ID
    title VARCHAR(500),
    author VARCHAR(255),                    -- Channel name
    transcript TEXT,                        -- Full transcript
    publish_date TIMESTAMP,
    duration INTEGER,                       -- Seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_video_id (video_id)
);

-- Messages table (chat history)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE SET NULL,
    role VARCHAR(20) NOT NULL,              -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
);

-- Session-Video association (many-to-many)
CREATE TABLE session_videos (
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (session_id, video_id)
);
```

### 3.2 Capacity Planning

**Assumptions** (toy project):
- 1 user (you)
- ~10 videos analyzed
- ~100 chat messages total
- Minimal growth

**Storage Estimates**:
- Users: 1 row × 100 bytes = 100 bytes
- Sessions: 5 sessions × 200 bytes = 1 KB
- Videos: 10 videos × (500 + avg transcript 50KB) = 505 KB
- Messages: 100 messages × 2KB avg = 200 KB
- **Total**: ~706 KB

**RDS Free Tier** (20 GB storage): More than sufficient for years.

**Database Connections**:
- FastAPI connection pool: 5-10 connections
- Single EC2 instance: Well within RDS limits

### 3.3 SQLAlchemy Models

Key relationships:
- One User → Many Sessions
- One Session → Many Messages
- One Session → Many Videos (via association table)
- One Video → Many Messages (optional reference)

---

## 4. API Specifications

### 4.1 Endpoints

**Base URL**: `http://<EC2_PUBLIC_IP>:8000/api/v1`

**Authentication**: All endpoints require `X-API-Key` header

#### POST /sessions
Create a new chat session.

**Request**:
```json
{}
```

**Response** (201 Created):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-11-22T10:30:00Z"
}
```

#### POST /sessions/{session_id}/videos
Submit a YouTube URL to a session.

**Request**:
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response** (200 OK):
```json
{
  "video_id": 123,
  "youtube_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "author": "Rick Astley",
  "duration": 213,
  "summary": "AI-generated summary of the video...",
  "added_at": "2025-11-22T10:31:00Z"
}
```

**Behavior**:
- Fetches transcript using youtube-transcript-api
- Calls Claude API to generate summary
- Stores video and summary in database
- Returns immediately (synchronous for MVP)

#### GET /sessions/{session_id}/videos
List all videos in a session.

**Response** (200 OK):
```json
{
  "videos": [
    {
      "video_id": 123,
      "youtube_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up",
      "author": "Rick Astley",
      "duration": 213,
      "added_at": "2025-11-22T10:31:00Z"
    }
  ]
}
```

#### POST /sessions/{session_id}/chat
Send a message and get AI response.

**Request**:
```json
{
  "message": "What is the main theme of this video?",
  "video_id": 123  // optional: context for which video
}
```

**Response** (200 OK):
```json
{
  "message_id": 456,
  "role": "assistant",
  "content": "The main theme is...",
  "created_at": "2025-11-22T10:32:00Z"
}
```

**Behavior**:
- Loads session history from database
- Loads video transcript if video_id provided
- Sends to Claude API with full context
- Saves both user message and assistant response
- Returns assistant response

#### GET /sessions/{session_id}/messages
Retrieve chat history.

**Query Params**:
- `limit`: Max messages to return (default: 50)
- `offset`: Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "messages": [
    {
      "message_id": 455,
      "role": "user",
      "content": "What is the main theme?",
      "created_at": "2025-11-22T10:31:50Z"
    },
    {
      "message_id": 456,
      "role": "assistant",
      "content": "The main theme is...",
      "created_at": "2025-11-22T10:32:00Z"
    }
  ],
  "total": 2,
  "has_more": false
}
```

#### GET /health
Health check endpoint (no auth required).

**Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-22T10:30:00Z"
}
```

### 4.2 Error Responses

**Standard error format**:
```json
{
  "error": {
    "code": "INVALID_VIDEO_URL",
    "message": "The provided URL is not a valid YouTube video",
    "details": {}
  }
}
```

**HTTP Status Codes**:
- 200: Success
- 201: Created
- 400: Bad Request (invalid input)
- 401: Unauthorized (missing/invalid API key)
- 404: Not Found
- 429: Too Many Requests (rate limit - Release 2)
- 500: Internal Server Error
- 503: Service Unavailable (DB connection failed)

---

## 5. Technology Stack

### 5.1 Backend
- **Framework**: FastAPI 0.115.5
- **ASGI Server**: uvicorn
- **ORM**: SQLAlchemy 2.x
- **Database Driver**: psycopg2-binary
- **Python Version**: 3.11

### 5.2 Database
- **Type**: PostgreSQL 15
- **Hosting**: AWS RDS (db.t3.micro)
- **Free Tier**: 750 hours/month, 20 GB storage

### 5.3 Deployment
- **Compute**: AWS EC2 t2.micro (free tier)
- **OS**: Ubuntu 24.04 LTS
- **Networking**: Public IP, HTTP (port 8000)
- **Future**: Docker containerization for ECS migration

### 5.4 External Services
- **AI**: Anthropic Claude API (claude-sonnet-4-5-20250929)
- **Video**: YouTube Transcript API
- **Monitoring**: AWS CloudWatch
- **Secrets**: AWS Parameter Store (free tier)

### 5.5 Development Tools
- **Formatting**: Black
- **Linting**: Ruff
- **Type Checking**: mypy (future)
- **Testing**: pytest (Release 2)
- **CI/CD**: GitHub Actions

---

## 6. Infrastructure & Deployment

### 6.1 AWS Resources

**EC2 Instance**:
- Type: t2.micro (1 vCPU, 1 GB RAM)
- AMI: Ubuntu 24.04 LTS
- Storage: 8 GB gp3 (free tier)
- Security Group: 
  - Inbound: SSH (22) from your IP
  - Inbound: HTTP (8000) from anywhere
  - Outbound: All traffic

**RDS Instance**:
- Type: db.t3.micro (2 vCPUs, 1 GB RAM)
- Engine: PostgreSQL 15
- Storage: 20 GB gp3
- Multi-AZ: No (single-AZ for free tier)
- Backup: 7 days retention
- Security Group:
  - Inbound: PostgreSQL (5432) from EC2 security group only

**CloudWatch**:
- Log Group: `/aws/ec2/youtube-research-tool`
- Metrics: CPU, Memory, Disk (standard EC2 metrics)
- Alarms: Error rate spike (Release 2)

**Budget Alert**:
- Monthly budget: $5
- Alert at 80% ($4)

### 6.2 Deployment Process

**Initial Setup**:
1. Provision RDS instance via AWS Console
2. Create database and apply schema
3. Launch EC2 instance
4. SSH into EC2, install dependencies
5. Clone repository from GitHub
6. Set environment variables
7. Run FastAPI with uvicorn
8. Test endpoints from local machine

**CI/CD Pipeline** (GitHub Actions):
1. On PR: Run linting and type checks
2. On merge to main:
   - SSH into EC2
   - Pull latest code
   - Install dependencies
   - Restart uvicorn service
   - Run health check

### 6.3 Configuration Management

**Environment Variables** (stored in AWS Parameter Store):
```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://postgres:password@rds-endpoint:5432/youtube_research
API_KEY=your-secret-api-key
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Local Development** (.env file, gitignored):
```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/youtube_research
API_KEY=dev-api-key
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

---

## 7. Security Requirements

### 7.1 Release 1 (Basic)
- ✅ API key authentication (simple header check)
- ✅ Secrets in AWS Parameter Store (not in code)
- ✅ Database credentials not hardcoded
- ✅ SQLAlchemy ORM (prevents SQL injection)
- ✅ CORS configured for specific origins
- ✅ Security groups restrict RDS access to EC2 only

### 7.2 Release 2 (Hardened)
- HTTPS with Let's Encrypt certificate
- Rate limiting (per IP, per API key)
- Input validation and sanitization
- Request size limits
- AWS Cognito for user authentication
- JWT token validation
- IAM roles for EC2 (no hardcoded AWS credentials)

---

## 8. Observability

### 8.1 Release 1 (Basic)
- ✅ Structured JSON logging to CloudWatch
- ✅ Log levels: DEBUG, INFO, WARNING, ERROR
- ✅ Log all API requests (method, path, status, duration)
- ✅ Health check endpoint
- ✅ Database connection status in health check

**Log Format**:
```json
{
  "timestamp": "2025-11-22T10:30:00.123Z",
  "level": "INFO",
  "logger": "api.main",
  "message": "POST /sessions/123/chat completed",
  "request_id": "abc-123",
  "status_code": 200,
  "duration_ms": 1234,
  "user_id": null
}
```

### 8.2 Release 2 (Enhanced)
- Custom CloudWatch metrics (request count, error rate, latency percentiles)
- CloudWatch Alarms (error rate > 5%, latency p95 > 5s)
- Dashboard with key metrics
- Distributed tracing with AWS X-Ray (optional)

---

## 9. Reliability

### 9.1 Release 1
- Stateless backend (can restart without data loss)
- Database persistence (survives crashes)
- Basic error handling (try/except, proper status codes)

### 9.2 Release 2
- Graceful shutdown (finish in-flight requests)
- Database connection pooling with retry logic
- Circuit breaker for external APIs
- Health checks with liveness/readiness probes
- Request timeout configuration
- Exponential backoff for Claude API retries

---

## 10. Code Quality

### 10.1 Release 1 (Required)
- ✅ Type hints throughout codebase
- ✅ Black formatting applied
- ✅ Ruff linting passes
- ✅ Docstrings for public functions
- ✅ Clear variable/function names
- ✅ DRY principle (no duplication)

### 10.2 Release 2 (Stretch)
- Unit tests (pytest) with >70% coverage
- Integration tests for API endpoints
- Pre-commit hooks for formatting/linting
- mypy type checking passes

---

## 11. Migration Path

### 11.1 Future: EC2 → ECS (Docker)
**Why**: Learn Docker, enable easier scaling, better resource utilization

**Steps**:
1. Create Dockerfile for FastAPI app
2. Build and test image locally
3. Push to Amazon ECR
4. Create ECS cluster and task definition
5. Deploy service to ECS
6. Update GitHub Actions to deploy to ECS
7. Decommission EC2 instance

### 11.2 Future: Async Background Jobs (Lambda)
**Why**: Offload slow operations (transcript fetching)

**Pattern**:
- POST /videos returns immediately with job_id
- Lambda triggered via SQS to fetch transcript
- Lambda updates database when complete
- GET /videos/{video_id} shows status (pending/complete)

---

## 12. Cost Management

### 12.1 Free Tier Usage (12 months)
- EC2 t2.micro: 750 hrs/month ✅
- RDS db.t3.micro: 750 hrs/month ✅
- RDS storage: 20 GB ✅
- CloudWatch: 5 GB logs ✅
- Parameter Store: Free ✅

**Expected Cost in Free Tier**: $0/month

### 12.2 After Free Tier (Month 13+)
- EC2 t2.micro: ~$8/month
- RDS db.t3.micro: ~$15/month
- RDS storage 20GB: ~$2/month
- CloudWatch: ~$1/month
- **Total**: ~$26/month

### 12.3 Cost Optimization
- Set AWS Budget Alert at $5/month
- Tag all resources: `Project=YouTubeResearchTool`, `Environment=Dev`
- Monthly cost review in AWS Cost Explorer
- **Migration option**: Move to EC2-local Postgres after month 12 (saves $17/month)

---

## 13. Decision Log

### 13.1 EC2 vs Lambda vs ECS

**Decision**: Start with EC2, migrate to ECS later

**Rationale**:
- Lambda timeout (15 min) problematic for long Claude API calls
- EC2 simplest for learning deployment
- ECS requires Docker knowledge (future learning goal)
- Free tier supports EC2 well

### 13.2 RDS vs EC2-local Postgres

**Decision**: Use RDS

**Rationale**:
- Professional/production pattern
- Managed backups and updates
- Separates compute from storage
- Free tier covers usage
- Can migrate to EC2-local after year 1 if needed

### 13.3 Synchronous vs Async Video Processing

**Decision**: Synchronous for MVP (POST /videos waits for completion)

**Rationale**:
- Simpler implementation
- Acceptable for single user
- Can add async (Lambda + SQS) in Release 2

### 13.4 API Key vs Cognito

**Decision**: API Key for Release 1, Cognito for Release 2

**Rationale**:
- Faster MVP
- Sufficient for single user testing
- Cognito adds complexity (user pools, JWT validation)
- Learning opportunity for Release 2

### 13.5 Communication Protocol: REST vs SSE vs WebSocket for LLM Streaming

**Decision**: Phased implementation - Build all three approaches to compare

**Implementation Plan**:
- **Phase 1**: Synchronous REST (Weeks 1-2)
- **Phase 1.5**: Server-Sent Events (SSE) streaming (Week 3)
- **Phase 2**: WebSocket bidirectional streaming (Week 4)

#### 13.5.1 Problem Statement

**Why Streaming Matters for LLMs**:

Modern LLM applications require token-by-token streaming for acceptable UX. Users now expect the "ChatGPT typing effect" where responses appear in real-time rather than after 10-30 second waits. This expectation has become the industry standard, making streaming a critical constraint for any LLM-powered application.

**Key Requirements**:
- Video transcripts can be 50KB+ (30-minute videos)
- Claude API processes and responds over 10-30 seconds
- Users expect to see tokens appearing immediately, not after full generation
- Perceived latency is more important than total latency
- Modern web applications compete against ChatGPT UX standards

**Future Vision: Agent Capabilities (V2)**:

During implementation planning, we identified that the ultimate vision for this application includes **autonomous agent capabilities**, not just a conversational interface. However, these features are **deferred to V2** to focus the initial implementation on protocol comparison and streaming fundamentals.

**Agent vs Chatbot (Future State)**:

| Dimension | Chatbot (V1) | Agent (V2 - Future) |
|-----------|--------------|---------------------|
| **Interaction model** | User asks → Bot responds | Agent takes autonomous actions |
| **Initiative** | Reactive only | Proactive + reactive |
| **Tool use** | None | Can call tools, modify state |
| **UI updates** | Response display only | Can push UI changes anytime |
| **Communication pattern** | Request-response | Bidirectional, event-driven |

**V2 Agent Features (Deferred)**:

These features are documented for future reference but **not implemented in V1**:

1. **Autonomous video discovery** (V2)
   - User: "Find videos about climate change"
   - Agent: "I found 3 videos, adding them now..." (adds videos in real-time)
   - Agent pushes UI updates to show new videos without page refresh
   - **Requires**: Claude tool use, WebSocket for server-initiated updates

2. **Natural language commands** (V2)
   - User: "Remove the third video" or "Search for solar energy videos"
   - Agent parses intent and executes commands
   - **Requires**: Intent parsing, multiple tools (add, remove, search, organize)

3. **Autonomous behavior** (V2)
   - Agent proactively searches for additional sources
   - Agent detects duplicates and removes them
   - Agent reorganizes workspace based on relevance
   - **Requires**: Agent decision-making loop, multi-tool orchestration

4. **UI manipulation** (V2 - Claude Artifacts style)
   - Agent renders custom visualizations
   - Agent reorganizes workspace layout
   - **Requires**: UI component framework, server→client UI commands

**V1 Implementation Focus**:

For the initial release, we're building a **streaming chatbot** (not agent):
- User submits messages
- System streams responses token-by-token
- No autonomous actions or tool use
- Focus on protocol comparison: REST → SSE → WebSocket

**Why Still Build WebSocket in V1?**

Even though agent features are deferred, we're still implementing WebSocket because:
1. **Learning objective**: Experience all three protocols firsthand
2. **Comparison data**: Need WebSocket metrics for Medium article
3. **Future-proofing**: V2 agent features will require WebSocket
4. **Best practices**: Understand production-grade real-time patterns
5. **Complete story**: Article needs all three patterns for credible comparison

The V1 WebSocket implementation will support basic bidirectional chat (user can send messages while receiving streams, interrupt generation), even without full agent autonomy.

#### 13.5.2 Options Evaluated

**Option A: AWS Lambda + API Gateway**

**Architecture**:
```
Client → API Gateway → Lambda → Claude API → Response
```

**Characteristics**:
- Serverless, automatic scaling
- AWS free tier: 1M requests/month
- Pay only for usage ($0.20 per 1M requests)
- 15-minute maximum timeout
- Cold start latency: 100-3000ms

**Verdict**: ❌ **Eliminated**

**Reasons for elimination**:
- Request-response model fights against streaming
- 15-minute timeout problematic for long-running LLM calls
- Cold starts add unacceptable latency to every chat message
- Streaming requires complex workarounds:
  - API Gateway WebSocket mode (complex setup)
  - EventBridge + polling (adds latency)
  - Step Functions orchestration (over-engineered)
- Keeping Lambda warm during 30s streaming window is expensive
- State management overhead (DynamoDB lookup per request)

**Option B: EC2 + FastAPI**

**Architecture**:
```
Client → EC2 (FastAPI) → Claude API → Stream tokens back
```

**Characteristics**:
- Persistent server (t2.micro)
- AWS free tier: 750 hours/month (24/7 operation)
- Native streaming support (HTTP/WebSocket)
- No cold starts
- In-memory state management
- Predictable $8/month cost after free tier

**Verdict**: ✅ **Selected**

**Reasons for selection**:
- Long-running processes support persistent streaming connections
- No timeout concerns for lengthy Claude API calls
- Simple deployment model for learning
- Native WebSocket and SSE support
- In-memory connection state (no database round-trips)
- Free tier covers 24/7 operation for 12 months

#### 13.5.3 Communication Protocol Comparison

Once EC2 was selected, three communication patterns were evaluated:

**Pattern 1: Synchronous REST**

**Implementation**:
```python
@app.post("/workspaces/{id}/messages")
def create_message(workspace_id: str, request: MessageRequest):
    # Wait for complete LLM response
    response = claude.messages.create(...)
    return {"content": response.content[0].text}
```

**Client experience**:
```javascript
const response = await fetch('/workspaces/123/messages', {
    method: 'POST',
    body: JSON.stringify({message: "Summarize this video"})
});
// User waits 10-30 seconds staring at loading spinner
const data = await response.json();
// All text appears at once
```

**Characteristics**:
- Simple implementation (standard REST patterns)
- Complete response returned after full generation
- User waits 10-30 seconds for any feedback
- All text appears instantly (no progressive rendering)

**Pros**:
- Simplest to implement and debug
- Standard HTTP patterns (works everywhere)
- Easy to test with curl/Postman
- No connection management complexity

**Cons**:
- Poor perceived performance (long loading spinner)
- User has no feedback during generation
- Feels slow compared to ChatGPT
- Doesn't meet modern UX expectations

**Pattern 2: Async REST + Polling**

**Implementation**:
```python
@app.post("/workspaces/{id}/messages")
def create_message(workspace_id: str, request: MessageRequest):
    # Return immediately with job ID
    job_id = background_jobs.submit(workspace_id, request.message)
    return {"job_id": job_id, "status": "processing"}, 201

@app.get("/workspaces/{id}/messages")
def get_messages(workspace_id: str, since: int = 0):
    # Poll for new messages
    messages = db.get_messages_since(workspace_id, since)
    return {"messages": messages}
```

**Client experience**:
```javascript
// Submit message
const {job_id} = await fetch('/workspaces/123/messages', {...});

// Poll every 1-2 seconds
const interval = setInterval(async () => {
    const response = await fetch('/workspaces/123/messages?since=456');
    if (response.messages.length > 0) {
        updateUI(response.messages);
        clearInterval(interval);
    }
}, 1500);
```

**Characteristics**:
- Client doesn't block on long HTTP request
- Background job processes LLM request
- Client polls periodically for updates
- 1-2 second granularity on updates

**Pros**:
- No long HTTP request timeout concerns
- Client remains responsive
- Simpler than WebSocket (uses standard HTTP)
- Works through all proxies/firewalls

**Cons**:
- Polling adds 1-2 second latency per update
- Many empty poll responses (wasteful)
- Chunky updates (can't do smooth token streaming)
- Can't achieve real-time typing effect
- Increased server load from constant polling
- Complexity of background job management

**Pattern 3: Server-Sent Events (SSE)**

**Implementation**:
```python
from fastapi.responses import StreamingResponse

@app.post("/workspaces/{id}/messages/stream")
def create_message_stream(workspace_id: str, request: MessageRequest):
    def event_generator():
        with claude.messages.stream(...) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'token': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Client experience**:
```javascript
const eventSource = new EventSource('/workspaces/123/messages/stream');
eventSource.onmessage = (event) => {
    const {token} = JSON.parse(event.data);
    appendToUI(token);  // Update happens < 10ms after token generation
};
```

**Characteristics**:
- Server pushes tokens as Claude API generates them
- One-way communication (server → client)
- Uses standard HTTP with persistent connection
- Built-in browser API (`EventSource`)
- Automatic reconnection on connection drop

**Pros**:
- Real-time token streaming (< 10ms latency)
- Smooth typing effect like ChatGPT
- Simple implementation (~15 lines of code)
- No polling overhead
- Automatic reconnection (resilient)
- Works through most proxies
- 90% of WebSocket benefits with 30% of complexity

**Cons**:
- One-way only (can't send messages mid-stream)
- Can't interrupt generation from client
- Connection stays open during generation
- Some corporate firewalls may block long connections
- **❌ Cannot support agent actions (V2 limitation)**: SSE can only push during an active response stream. Future agent features would require:
  - Add videos to workspace mid-conversation (V2)
  - Push UI updates outside of response context (V2)
  - Initiate actions without user request (V2)
  - Send background job completion notifications (V2)

**Future Agent Use Case Limitation (V2)**:

SSE works for streaming chatbots (V1) but would fail for autonomous agents (V2):

```javascript
// What SSE can do (V1):
User: "Summarize these videos"
→ Server streams tokens: "The videos discuss..."

// What SSE cannot do (V2 - deferred):
Agent (autonomous): "I found related videos, adding them now..."
→ ❌ No way to push this action outside request context
→ ❌ Cannot update UI without new request
→ ❌ Cannot implement agent tool use
```

This limitation makes SSE suitable for **V1 chatbot streaming** but would be insufficient for **V2 agent autonomy**.

**Pattern 4: WebSocket**

**Implementation**:
```python
from fastapi import WebSocket

@app.websocket("/workspaces/{id}/ws")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await websocket.accept()
    while True:
        # Receive message from client
        data = await websocket.receive_json()

        # Stream tokens back
        async with claude.messages.stream(...) as stream:
            async for text in stream.text_stream:
                await websocket.send_json({"type": "token", "content": text})

        await websocket.send_json({"type": "done"})
```

**Client experience**:
```javascript
const ws = new WebSocket('ws://localhost:8000/workspaces/123/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'token') {
        appendToUI(data.content);
    }
};

// Can send new messages anytime
ws.send(JSON.stringify({message: "Tell me more"}));

// Can interrupt mid-generation
ws.send(JSON.stringify({command: "stop"}));
```

**Characteristics**:
- Full-duplex bidirectional communication
- Custom protocol (ws:// or wss://)
- Persistent connection with stateful session
- Low-latency message passing

**Pros**:
- True real-time bidirectional streaming
- Can interrupt generation mid-stream (V1)
- Can send follow-up questions before response completes (V1)
- Lower latency than SSE (connection reuse)
- Full control over connection lifecycle
- Production-grade real-time patterns
- **✅ Enables future agent actions (V2)**: WebSocket allows:
  - Agent-initiated UI updates anytime (V2)
  - Server-side tool use with live feedback (V2)
  - Background job notifications (V2)
  - Real-time workspace modifications (V2)
  - Persistent bidirectional channel for agent autonomy (V2)

**Cons**:
- More complex implementation (connection management, heartbeats)
- Manual reconnection logic required
- Protocol upgrade (not pure HTTP)
- Some proxies/firewalls block WebSocket
- Requires more client-side code
- Stateful connections harder to scale

**V1 Use Cases (Implemented)**:

Basic bidirectional chat patterns:

```javascript
// V1: User can send messages during streaming response
User → WS: {message: "Summarize these videos"}
Server → WS: {type: "token", content: "The"}
Server → WS: {type: "token", content: " videos"}
Server → WS: {type: "token", content: " discuss..."}

// User interrupts mid-stream
User → WS: {command: "stop"}
Server → WS: {type: "cancelled"}

// User sends follow-up before response completes
User → WS: {message: "Focus on climate change"}
```

**V2 Use Cases (Future - Deferred)**:

Future agent autonomy patterns (not implemented in V1):

```javascript
// V2 Example 1: Agent autonomous video discovery (DEFERRED)
User → WS: {message: "Find videos about climate change"}

Agent → WS: {type: "token", content: "I'll search for climate change videos..."}
Agent → WS: {type: "action", action: "add_video", video: {...}}
Agent → WS: {type: "ui_update", component: "video_list", data: {...}}
Agent → WS: {type: "token", content: "I've added 3 videos to your workspace."}
```

```javascript
// V2 Example 2: Agent proactive cleanup (DEFERRED)
Agent → WS: {
    type: "token",
    content: "I noticed you have duplicate videos. Removing them..."
}
Agent → WS: {type: "action", action: "remove_video", video_id: 456}
Agent → WS: {type: "ui_update", component: "video_list", action: "remove", id: 456}
```

```javascript
// V2 Example 3: Background job completion (DEFERRED)
Agent → WS: {
    type: "notification",
    message: "Transcript processing complete for 'AI Overview'"
}
Agent → WS: {type: "ui_update", component: "video_card", video_id: 789, data: {...}}
```

These V2 agent patterns are **only possible with WebSocket**. SSE cannot support server-initiated actions outside of an active response stream. However, these features are **deferred to V2** - the V1 implementation focuses on basic streaming and bidirectional chat.

#### 13.5.4 Comparison Matrix

| Dimension | Sync REST | Async + Poll | SSE | WebSocket |
|-----------|-----------|--------------|-----|-----------|
| **User Experience** |
| Time to first token | N/A (full wait) | 1-2s (poll delay) | ~50ms | ~30ms |
| Perceived latency | 10-30s | 1-2s chunky | Real-time | Real-time |
| UX quality | ⭐ Poor | ⭐⭐ Acceptable | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Best |
| Meets ChatGPT standard | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Technical** |
| Implementation complexity | ⭐ Simplest | ⭐⭐⭐ Medium | ⭐⭐ Easy | ⭐⭐⭐⭐ Complex |
| Lines of code (estimate) | 20 | 60 | 35 | 80 |
| Protocol | HTTP | HTTP | HTTP (persistent) | WebSocket (ws://) |
| Connection model | Request-response | Request-response | Server push | Full duplex |
| Client API | `fetch()` | `fetch()` + polling | `EventSource` | `WebSocket` |
| **Operational** |
| Proxy compatibility | ✅ Universal | ✅ Universal | ✅ Most | ⚠️ Some block |
| Firewall compatibility | ✅ All | ✅ All | ✅ Most | ⚠️ Some block |
| Auto-reconnection | N/A | N/A | ✅ Built-in | ❌ Manual |
| Error handling | Standard HTTP | Standard HTTP | Auto-retry | Custom logic |
| Server resource usage | Low | Medium (polling) | Medium (persistent) | Medium (persistent) |
| **Capabilities (V1)** |
| Streaming tokens | ❌ | ❌ | ✅ | ✅ |
| Mid-stream cancellation | ❌ | ⚠️ Delayed | ❌ | ✅ |
| Bidirectional | ❌ | ❌ | ❌ | ✅ |
| Server-initiated push | ❌ | ❌ | ⚠️ During stream | ✅ Anytime |
| **Agent Features (V2 - Deferred)** |
| Autonomous tool use | ❌ | ❌ | ❌ | ✅ Possible |
| Agent-initiated UI updates | ❌ | ❌ | ❌ | ✅ Possible |
| Proactive actions | ❌ | ❌ | ❌ | ✅ Possible |
| Background notifications | ❌ | ⚠️ Poll only | ❌ | ✅ Possible |

#### 13.5.5 The Phased Implementation Decision

**Decision**: Build all three patterns sequentially for learning and comparison

**Phase 1: Synchronous REST** (Weeks 1-2)
- Implement standard REST endpoints
- Focus on domain logic, DDD patterns, data models
- Establish baseline measurements
- Simplest debugging environment
- Working product quickly

**Deliverables**:
- `POST /workspaces/{id}/messages` - synchronous
- Full domain layer implementation
- Database persistence
- End-to-end functionality

**Phase 1.5: Server-Sent Events** (Week 3)
- Add streaming endpoint alongside synchronous
- Integrate Anthropic SDK streaming
- Implement token-by-token delivery
- Measure perceived performance improvement
- Modern UX with minimal code changes

**Deliverables**:
- `POST /workspaces/{id}/messages/stream` - SSE streaming
- Real-time token streaming
- Performance metrics collection
- Side-by-side comparison with Phase 1

**Phase 2: WebSocket** (Week 4)
- Implement full bidirectional WebSocket
- Add mid-stream cancellation
- Connection lifecycle management
- Production-grade real-time patterns
- Complete comparison data

**Deliverables**:
- `WS /workspaces/{id}/ws` - WebSocket endpoint
- Bidirectional messaging
- Interruption/cancellation support
- Connection state management
- Complete performance comparison

**Rationale for phased approach**:

1. **Progressive learning**: Each phase builds on previous knowledge
   - Phase 1: Master domain logic without streaming complexity
   - Phase 1.5: Learn one-way streaming (simpler)
   - Phase 2: Master bidirectional streaming (complex)

2. **Working software always**: Each phase produces usable product
   - Never blocked by streaming complexity
   - Can deploy and test after each phase
   - Incremental value delivery

3. **Comparison data**: Experience all patterns firsthand
   - Feel the UX difference viscerally
   - Measure real latency numbers
   - Understand trade-offs empirically
   - Make informed recommendations

4. **Article content**: Rich material for Medium article
   - Three complete implementations to compare
   - Real metrics from production-like environment
   - Code examples from actual working system
   - Authentic insights from building all approaches

5. **Production optionality**: Multiple deployment options
   - Simple applications: Ship with sync REST
   - Most applications: Ship with SSE (90% solution)
   - Complex applications: Ship with WebSocket (full features)

#### 13.5.6 Measurement Criteria

**Metrics to collect for each phase**:

**Performance Metrics**:
- Time to first token (P50, P95, P99)
- Total response time
- Token throughput (tokens/second)
- Perceived latency (user-facing)
- Server resource usage (CPU, memory)
- Network bandwidth consumption

**Complexity Metrics**:
- Lines of code (backend)
- Lines of code (client)
- Number of files modified
- Implementation time (developer hours)
- Debugging difficulty (subjective 1-5 scale)

**Reliability Metrics**:
- Error rate under normal conditions
- Behavior on connection drop
- Recovery time after failure
- Cross-browser compatibility
- Proxy/firewall compatibility

**User Experience Metrics** (subjective testing):
- Perceived speed (1-5 scale)
- Comparison to ChatGPT UX (1-5 scale)
- Frustration during generation (1-5 scale)
- Willingness to wait (yes/no)

**Example measurement table**:

| Metric | Sync REST | SSE | WebSocket |
|--------|-----------|-----|-----------|
| Time to first token | 12,450ms | 52ms | 34ms |
| Total time (500 tokens) | 12,450ms | 12,500ms | 12,480ms |
| Perceived speed (1-5) | 1.5 | 4.5 | 4.8 |
| Implementation time | 4 hours | 6 hours | 12 hours |
| Client LOC | 25 | 35 | 65 |
| Backend LOC | 40 | 55 | 95 |

#### 13.5.7 Technical Implementation Notes

**SSE Implementation Details**:

Server (FastAPI):
```python
from fastapi.responses import StreamingResponse
import json

@app.post("/workspaces/{workspace_id}/messages/stream")
async def stream_message(workspace_id: str, request: MessageRequest):
    async def event_stream():
        # Load conversation history
        session = await load_session(workspace_id)

        # Stream from Claude API
        async with claude.messages.stream(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            system=session.system_prompt,
            messages=session.messages + [{"role": "user", "content": request.content}]
        ) as stream:
            async for text in stream.text_stream:
                yield f"data: {json.dumps({'token': text})}\n\n"

        # Signal completion
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

Client (JavaScript):
```javascript
const eventSource = new EventSource(
    '/workspaces/123/messages/stream',
    { withCredentials: true }
);

let fullResponse = "";

eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
        eventSource.close();
        return;
    }

    const {token} = JSON.parse(event.data);
    fullResponse += token;
    updateUI(fullResponse);  // Progressive rendering
};

eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    eventSource.close();
};
```

**WebSocket Implementation Details**:

Server (FastAPI):
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/workspaces/{workspace_id}/ws")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await websocket.accept()

    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_json()

            if data.get("command") == "stop":
                break

            # Stream response
            async with claude.messages.stream(...) as stream:
                async for text in stream.text_stream:
                    await websocket.send_json({
                        "type": "token",
                        "content": text
                    })

                    # Check for stop command
                    if await check_stop_requested(websocket):
                        stream.cancel()
                        break

            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        print(f"Client disconnected from workspace {workspace_id}")
```

Client (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8000/workspaces/123/ws');

let fullResponse = "";

ws.onopen = () => {
    // Send initial message
    ws.send(JSON.stringify({
        message: "Summarize this video"
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'token') {
        fullResponse += data.content;
        updateUI(fullResponse);
    } else if (data.type === 'done') {
        console.log('Generation complete');
    }
};

// Can interrupt mid-generation
function stopGeneration() {
    ws.send(JSON.stringify({command: "stop"}));
}

// Manual reconnection logic
ws.onclose = () => {
    console.log('Connection closed, reconnecting...');
    setTimeout(connectWebSocket, 1000);
};
```

#### 13.5.8 When to Use Each Pattern (Decision Framework)

**Use Synchronous REST when**:
- Building MVP/prototype rapidly
- Responses are fast (< 2 seconds)
- Users don't expect real-time feedback
- Simplicity is paramount
- **Application type**: Simple request-response APIs
- Example: Admin dashboards, batch processing APIs, CRUD operations

**Use Polling when**:
- Need maximum compatibility (works everywhere)
- Updates are infrequent (every 5-30 seconds acceptable)
- Cannot use persistent connections (corporate firewall restrictions)
- Building for legacy systems
- **Application type**: Status checking, batch job monitoring
- Example: Job status polling, occasional updates

**Use SSE when**:
- Streaming LLM responses (chatbot pattern)
- Server needs to push updates during active request
- One-way communication is sufficient
- Want 90% of WebSocket benefits with minimal complexity
- Most proxies/firewalls must work
- **Application type**: Streaming chatbots, live feeds, progress indicators
- Example: ChatGPT-style interfaces (response streaming only), stock tickers, log streaming, LLM token streaming

**Use WebSocket when**:
- Need bidirectional real-time communication
- Users must interrupt/cancel operations mid-stream (V1)
- Want lowest latency for real-time chat (V1)
- **Building autonomous agents with tool use (V2)**
- Agent needs to take actions without user prompts (V2)
- Server must initiate UI updates anytime (V2)
- Building complex real-time features
- Can handle connection management complexity
- **Application type**: Bidirectional chat, agents (V2), collaborative apps, real-time games
- Example: Chat with interruption, AI agents with tool use (V2), collaborative editing, gaming, trading platforms

**The Critical Distinction: Chatbot (V1) vs Agent (V2)**

| Feature | Use SSE | Use WebSocket |
|---------|---------|---------------|
| **Simple chatbot (V1)** | ✅ Sufficient | ✅ Better (interruption) |
| User asks → Bot responds | ✅ | ✅ |
| Stream response tokens | ✅ | ✅ |
| Interrupt generation mid-stream | ❌ | ✅ V1 |
| **Autonomous agent (V2 - deferred)** | ❌ Cannot do | ✅ Required |
| Agent searches and adds videos | ❌ | ✅ V2 possible |
| Agent modifies UI proactively | ❌ | ✅ V2 possible |
| Agent uses tools autonomously | ❌ | ✅ V2 possible |
| Background job notifications | ❌ | ✅ V2 possible |

**Recommendation for LLM applications**:

1. **If building a simple chatbot** (V1 scope):
   - SSE is sufficient for basic streaming
   - WebSocket adds interruption capability and future-proofing
   - Start with SSE if complexity is a concern
   - Use WebSocket if you want production-grade bidirectional patterns

2. **If building an agent** (V2 scope):
   - **WebSocket is required** (not optional)
   - Agent autonomy demands bidirectional communication
   - SSE fundamentally cannot support agent patterns
   - Plan for WebSocket from the start

**This Project - V1 Scope**: We're building a **streaming chatbot** with three implementations for comparison:
- Phase 1: REST + Polling (baseline comparison)
- Phase 1.5: SSE (sweet spot for chatbot streaming)
- Phase 2: WebSocket (enables interruption + future V2 agent features)

We're building all three phases to:
- Document the limitations of each approach
- Create comparison content for Medium article
- Understand when simpler patterns are sufficient
- Experience the differences firsthand
- Future-proof for V2 agent capabilities

#### 13.5.9 Expected Outcomes for Medium Article

**Primary Article: Polling vs SSE vs WebSocket**

**Article Title Ideas**:
- "I Built an LLM Chat App 3 Ways: Polling vs SSE vs WebSocket"
- "REST Polling, SSE, or WebSocket? I Tested All Three for LLM Streaming"
- "Comparing Communication Patterns for Real-Time LLM Applications"
- "From Polling to WebSocket: Choosing the Right Protocol for LLM Streaming"

**Article structure**:
1. **Introduction**: The problem - streaming LLM responses for good UX
   - 10-30 second response times are unacceptable
   - Users expect ChatGPT-style streaming
   - Need to choose a communication pattern

2. **The Setup**: Building a YouTube video analysis tool with Claude API
   - Requirements: Stream LLM responses, enable agent actions
   - Decision to build all three patterns to compare

3. **Pattern 1: Async REST + Polling**
   - How it works: POST returns job ID, client polls for updates
   - Code example (server + client)
   - Pros: Simple, works everywhere, no special protocols
   - Cons: 1-2s latency per poll, wasteful, chunky updates
   - Measurements: Implementation time, perceived latency
   - **Verdict**: Works but inefficient, poor UX

4. **Pattern 2: Server-Sent Events (SSE)**
   - How it works: HTTP streaming with EventSource API
   - Code example (server + client)
   - Pros: Real-time streaming, simple, auto-reconnect, 90% solution
   - Cons: One-way only, limited for bidirectional needs
   - Measurements: Time to first token, implementation complexity
   - **Verdict**: Perfect for streaming responses, but has limitations

5. **Pattern 3: WebSocket**
   - How it works: Full-duplex bidirectional communication
   - Code example (server + client with agent actions)
   - Pros: Bidirectional, enables autonomous actions, lowest latency
   - Cons: More complex, manual reconnection, some firewall issues
   - Measurements: Complete feature set, connection overhead
   - **Verdict**: Required for advanced features, worth the complexity

6. **Side-by-Side Comparison**
   - Comparison table with all dimensions
   - Performance metrics across all three
   - Implementation complexity comparison
   - When each pattern breaks down

7. **Decision Framework**: When to use each
   - Use Polling when: Maximum compatibility, simple APIs, infrequent updates
   - Use SSE when: Streaming responses, server-to-client push, most LLM apps
   - Use WebSocket when: Bidirectional communication, agent actions, real-time collaboration

8. **Lessons Learned**
   - SSE is the sweet spot for most LLM streaming
   - WebSocket necessary for advanced agent features
   - Polling still has its place for simple use cases
   - Build incrementally: Start simple, add complexity as needed

9. **Conclusion**: Choose based on your requirements, not hype
   - Most apps should start with SSE
   - WebSocket when you need bidirectional features
   - All three have valid use cases

**Key insights to highlight**:
- Perceived latency > total latency for user satisfaction
- SSE provides 90% of WebSocket benefits with 30% of complexity for one-way streaming
- Polling is inefficient but works everywhere (good fallback)
- WebSocket enables bidirectional patterns that SSE cannot support
- Modern LLM UX standards are now non-negotiable
- Progressive implementation (phases) aids learning
- Build all three to viscerally understand the trade-offs

**Target audience takeaways**:
1. Start with SSE for LLM streaming (best ROI)
2. Use WebSocket when you need bidirectional communication
3. Keep polling as a fallback for maximum compatibility
4. Match the protocol to your requirements, not the latest trend

**Code examples to include**:
- Polling implementation (POST + GET loop)
- SSE streaming (FastAPI StreamingResponse + EventSource)
- WebSocket (bidirectional with agent actions)
- Performance measurement code
- Side-by-side client comparisons

**Measurements to present**:
- Time to first token (Polling: 1-2s, SSE: 50ms, WS: 30ms)
- Total response time (all ~12-13s for 500 tokens)
- Implementation complexity (LOC, developer hours)
- Perceived UX quality (subjective ratings)
- When each pattern fails (concrete examples)

**Future Article Ideas** (separate articles):
- "Chatbot vs Agent: Why WebSocket Becomes Non-Negotiable"
- "Building Autonomous LLM Agents: Architecture Patterns"
- "Lambda vs EC2 for LLM Streaming: A Cost-Benefit Analysis"
- "Implementing Claude Tool Use in a Real-Time Agent"

---

## 14. V2 Features (Deferred Agent Capabilities)

### 14.1 Overview

The V1 implementation focuses on protocol comparison and streaming chatbot capabilities. Advanced agent features requiring autonomous actions, tool use, and proactive behaviors are **deferred to V2**. This section documents these features for future reference.

### 14.2 V2 Feature Set

#### 14.2.1 Tool Use Pattern

**Description**: Agent can execute tools during conversation using Claude API function calling.

**Example**:
```
User: "Add this video: youtube.com/watch?v=abc"
Agent: [calls add_video tool via Claude]
Agent: [pushes video to client via WebSocket]
Agent: "I've added the video about climate change"
```

**Requirements**:
- Claude API tool/function calling integration
- WebSocket for server-initiated updates
- Tool execution framework (add_video, remove_video, search_videos)
- Error handling for tool failures

**Implementation Effort**: Medium (15-20 hours)

#### 14.2.2 Natural Language Commands

**Description**: Agent parses user intent and executes corresponding commands.

**Examples**:
```
User: "Remove the third video"
User: "Search for videos about solar energy"
User: "Organize these by topic"
```

**Requirements**:
- Intent parsing (can use Claude's natural language understanding)
- Multiple tool implementations:
  - `add_video(url)`: Add video by URL
  - `remove_video(index|id)`: Remove video by position or ID
  - `search_videos(query)`: Search YouTube
  - `organize_videos(strategy)`: Reorder by relevance/date/topic
- Command validation and error handling

**Implementation Effort**: Medium-Large (20-30 hours)

#### 14.2.3 Autonomous Behavior

**Description**: Agent makes proactive decisions without explicit user requests.

**Example**:
```
User: "What's the consensus on climate change?"

Agent thinks: "I need more sources to provide accurate consensus"
Agent: [autonomously searches YouTube for climate change videos]
Agent: [adds 5 relevant videos to workspace]
Agent: "I just added 5 videos for comprehensive analysis. Based on these sources, the consensus is..."
```

**Requirements**:
- Agent decision-making loop (when to search, how many sources)
- Multi-tool orchestration (search → filter → add → analyze)
- Heuristics for "good enough" data
- User notification of autonomous actions
- Ability to undo agent actions

**Implementation Effort**: Large (30-40 hours)

**Challenges**:
- Defining when agent should act autonomously vs ask for permission
- Preventing runaway behavior (agent adding too many videos)
- Cost control (Claude API calls for decision-making)

#### 14.2.4 UI Manipulation (Claude Artifacts Style)

**Description**: Agent can render custom UI components and manipulate workspace layout.

**Examples**:
```
Agent: "Here's a comparison chart I created"
[Renders interactive visualization comparing video viewpoints]

Agent: "I've reorganized your workspace into sections"
[UI updates with videos grouped by topic]
```

**Requirements**:
- UI component framework (charts, tables, custom layouts)
- Protocol for server→client UI commands
- Component registry (what components can be rendered)
- Client-side rendering engine
- State synchronization (server knows what UI is displayed)

**Implementation Effort**: Very Large (40-60 hours)

**Challenges**:
- Defining safe/allowed UI manipulations
- Security (prevent malicious UI injections)
- Component versioning (client must support server's components)
- Complexity of custom visualizations

### 14.3 V2 Architecture Changes

**Database Schema Changes**:
```sql
-- Tool execution log
CREATE TABLE tool_executions (
    id SERIAL PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id),
    tool_name VARCHAR(100),
    parameters JSONB,
    result JSONB,
    success BOOLEAN,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent actions history (for undo/audit)
CREATE TABLE agent_actions (
    id SERIAL PRIMARY KEY,
    workspace_id UUID REFERENCES workspaces(id),
    action_type VARCHAR(50),  -- 'add_video', 'remove_video', 'search'
    details JSONB,
    undoable BOOLEAN DEFAULT true,
    undo_action JSONB,  -- How to reverse this action
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**API Changes**:
- New WebSocket message types: `tool_call`, `tool_result`, `ui_component`
- Agent decision-making service (when to act autonomously)
- Tool registry and execution framework
- Undo/redo functionality

**Claude Integration**:
- Implement Claude tool use (function calling)
- Define tool schemas for Claude
- Parse Claude tool call responses
- Execute tools and return results to Claude

### 14.4 V2 Implementation Timeline

**Estimated Effort**: 100-150 hours total

**Suggested Phases**:
1. **V2.1**: Tool use pattern (20h)
   - Basic tool execution framework
   - Claude function calling integration
   - WebSocket message types for tools

2. **V2.2**: Natural language commands (25h)
   - Implement core tools (add, remove, search, organize)
   - Command validation and error handling
   - User feedback on command execution

3. **V2.3**: Autonomous behavior (35h)
   - Agent decision-making logic
   - Multi-tool orchestration
   - Cost control and safety limits
   - Undo functionality

4. **V2.4**: UI manipulation (40h)
   - Component framework
   - Rendering engine
   - Custom visualizations
   - Security validation

### 14.5 V2 Prerequisites

Before implementing V2, complete:
- ✅ V1 WebSocket implementation (baseline architecture)
- ✅ Workspace domain model (understand state management)
- ✅ Claude API streaming integration (foundational)
- ⬜ Frontend framework decision (React/Vue/Svelte)
- ⬜ Component library selection (for UI manipulation)
- ⬜ Cost monitoring for Claude API (before autonomous behavior)

### 14.6 V2 Decision Point

**When to implement V2**:
- V1 is stable and users are requesting agent features
- Budget allows for increased Claude API usage
- Team has capacity for 100-150h effort
- Frontend framework is mature enough for dynamic components

**Alternatives to full V2**:
- Implement only V2.1-V2.2 (tool use + commands) without autonomy
- Use manual commands instead of autonomous behavior
- Skip UI manipulation (keep it simple)

---

## 15. Open Questions & Risks

### 15.1 Open Questions
- **Frontend integration timeline**: When to connect Next.js?
- **Video processing timeout**: What if transcript fetch takes >30s?
- **Claude API rate limits**: Need to understand quotas

### 15.2 Risks

| Risk | Impact | Mitigation |
|------|--------|----------|
| RDS free tier expires in 12 months | $17/month cost | Budget alert, migration plan to EC2-local Postgres |
| Claude API costs exceed budget | High costs | Monitor usage, implement request caching |
| EC2 instance crashes frequently | Service downtime | CloudWatch alarms, auto-restart with systemd |
| Transcript API unreliable | Failed video processing | Retry logic, error handling |

---

## 15. Timeline & Milestones

### Release 1: MVP Backend (Estimated: 1-2 weeks)

**Week 1: Local Development**
- Day 1-2: Database setup (schema, models, connections)
- Day 3-4: FastAPI endpoints implementation
- Day 5-6: Integration with existing services
- Day 7: Local end-to-end testing

**Week 2: AWS Deployment**
- Day 1: Provision RDS and EC2
- Day 2: Deploy application to EC2
- Day 3: Configure CloudWatch logging
- Day 4: Set up GitHub Actions CI/CD
- Day 5: Remote testing and bug fixes
- Day 6-7: Documentation and handoff

### Release 2: Polish & Hardening (Estimated: 1 week)
- Security hardening
- Observability enhancements
- Reliability improvements
- Testing coverage

---

## 16. Appendices

### 16.1 Glossary
- **Agent**: An autonomous AI system that can take proactive actions, use tools, and modify application state without explicit user requests. Contrast with chatbot (reactive only).
- **API**: Application Programming Interface
- **Chatbot**: A reactive conversational interface that responds to user requests but takes no autonomous actions. Contrast with agent.
- **EC2**: Elastic Compute Cloud (AWS virtual servers)
- **RDS**: Relational Database Service (managed database)
- **ORM**: Object-Relational Mapping (SQLAlchemy)
- **JWT**: JSON Web Token (authentication)
- **CORS**: Cross-Origin Resource Sharing
- **SSE**: Server-Sent Events (HTTP streaming protocol for server-to-client push)
- **WebSocket**: Full-duplex communication protocol over TCP
- **Token**: In LLM context, a piece of text (word fragment) generated by the model
- **Tool use**: Agent capability to call functions/APIs to perform actions (search, add videos, modify state)

### 16.2 References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI WebSocket Support](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [AWS RDS Free Tier](https://aws.amazon.com/rds/free/)
- [AWS EC2 Free Tier](https://aws.amazon.com/ec2/pricing/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Anthropic Streaming](https://docs.anthropic.com/en/api/streaming)
- [Anthropic Tool Use (Function Calling)](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MDN: WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

### 16.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-22 | Eric | Initial version |
| 1.1 | 2025-12-04 | Eric | Added section 13.5: Communication Protocol decision (REST/SSE/WebSocket comparison), phased implementation plan, and Medium article preparation |
| 1.2 | 2025-12-04 | Eric | Clarified V1 scope (streaming chatbot) vs V2 scope (autonomous agent). Added section 14: V2 Features documenting deferred agent capabilities (tool use, natural language commands, autonomous behavior, UI manipulation). Updated all protocol comparisons to distinguish V1 vs V2 requirements. |

---

**End of Document**
