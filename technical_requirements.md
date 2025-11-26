# Technical Requirements Document
## YouTube Research Tool - Console to Backend Service Conversion

**Version**: 1.0  
**Date**: November 22, 2025  
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

---

## 14. Open Questions & Risks

### 14.1 Open Questions
- **Frontend integration timeline**: When to connect Next.js?
- **Video processing timeout**: What if transcript fetch takes >30s?
- **Claude API rate limits**: Need to understand quotas

### 14.2 Risks

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
- **API**: Application Programming Interface
- **EC2**: Elastic Compute Cloud (AWS virtual servers)
- **RDS**: Relational Database Service (managed database)
- **ORM**: Object-Relational Mapping (SQLAlchemy)
- **JWT**: JSON Web Token (authentication)
- **CORS**: Cross-Origin Resource Sharing

### 16.2 References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [AWS RDS Free Tier](https://aws.amazon.com/rds/free/)
- [AWS EC2 Free Tier](https://aws.amazon.com/ec2/pricing/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

### 16.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-22 | Eric | Initial version |

---

**End of Document**
