# Architecture Comparison - Watch and Summarize Flow

## How to Read These Diagrams

**Participants are grouped by architectural layer:**
- **API Layer (left box):** HTTP interface (FastAPI routes)
- **Domain Layer (middle box):** Business logic (services, agents)
- **Infrastructure Layer (right box):** Technical implementations (databases, external APIs)

**Dependency rules for Clean Architecture:**
- ✓ **API → Domain:** API can call Domain (correct)
- ✓ **Infrastructure → Domain:** Infrastructure implements Domain interfaces (correct - dependency inversion)
- ❌ **Domain → Infrastructure:** Domain should NOT import/create Infrastructure classes (violation)
- ✓ **Domain → Domain:** Domain can call other Domain components (correct)

**Look for arrows crossing boundaries the wrong way.**

---

## Current Architecture (As-Is with Events)

```mermaid
sequenceDiagram
    participant User

    box API Layer
        participant API as FastAPI Route
    end

    box Domain Layer
        participant WS as WorkspaceService
        participant Agent as ChatAgent
        participant TE as ToolExecutor
        participant ChatApp as ChatApplication
    end

    box Infrastructure Layer
        participant YT as YouTubeService
        participant SB as SummaryBot
        participant VR as VideoRepository
        participant DB as PostgreSQL
    end

    User->>API: POST /messages "Watch and summarize video X"
    API->>WS: send_message(workspace_id, message)

    Note over WS: Create on_event callback
    WS->>Agent: ChatAgent(on_event=save_callback)
    WS->>Agent: chat(message)

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: watch_video(url)

    Agent->>TE: execute_tool("watch_video", args)
    TE->>ChatApp: watch_video(url)
    ChatApp->>YT: get_video(url)
    YT-->>ChatApp: video object

    Note over ChatApp: Store in videos list
    ChatApp->>ChatApp: videos.append(video)

    Note over ChatApp: Fire event
    ChatApp->>WS: on_event(AgentEvent: video_watched)
    WS->>VR: save_video(workspace_id, video_dict)
    VR->>DB: INSERT video, workspace_video
    DB-->>VR: video_id
    VR-->>WS: saved

    ChatApp-->>TE: "Watched video X. Id is 0"
    TE-->>Agent: tool_result

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: get_summary(0)

    Agent->>TE: execute_tool("get_summary", {id: 0})
    TE->>ChatApp: get_summary(0)

    Note over ChatApp: Get from in-memory list
    ChatApp->>ChatApp: video = videos[0]

    ChatApp->>SB: summarize_transcript(transcript)
    SB-->>ChatApp: summary text

    Note over ChatApp: Fire event
    ChatApp->>WS: on_event(AgentEvent: video_summarized)
    WS->>VR: save_summary(workspace_id, video_id, summary)
    VR->>DB: UPDATE workspace_video SET summary
    DB-->>VR: success

    ChatApp-->>TE: summary text
    TE-->>Agent: tool_result

    Agent->>Agent: Claude API call
    Note over Agent: Final response

    Agent-->>WS: AgentResult
    WS-->>API: final_response
    API-->>User: 200 OK with response
```

**Problems:**
- ChatApplication holds videos in memory (array index 0)
- Must pre-load all videos before agent starts
- Video ID from database not used by tools
- Events fired for side effects, handled by callback
- State lost after agent finishes

**Boundary Violations (Wrong Dependencies):**
- ❌ ChatApp → YT (Domain imports and creates Infrastructure directly)
- ❌ ChatApp → SB (Domain imports and creates Infrastructure directly)
- ❌ Line 30 in chat_appllcation.py: `self.youtube = YouTubeService()` (Domain creates Infrastructure)
- ❌ Line 14 in chat_appllcation.py: `self.summary_bot = YouTubeSummaryBot()` (Domain creates Infrastructure)
- ✓ API → Domain (correct direction)
- ✓ Domain → Infrastructure via callback (acceptable pattern, though not pure dependency inversion)

---

## DDD Architecture (To-Be without Events)

```mermaid
sequenceDiagram
    participant User

    box API Layer
        participant API as FastAPI Route
    end

    box Domain Layer
        participant WS as WorkspaceService
        participant Agent as ChatAgent
        participant Tools as Tool Handler
    end

    box Infrastructure Layer
        participant YT as YouTubeService
        participant SB as SummaryBot
        participant VR as VideoRepository
        participant DB as PostgreSQL
    end

    User->>API: POST /messages "Watch and summarize video X"
    API->>WS: send_message(workspace_id, message)

    Note over WS: Create tool handler
    WS->>Agent: ChatAgent(workspace_id, tool_handler)
    WS->>Agent: chat(message)

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: watch_video(url)

    Agent->>Tools: execute("watch_video", {url})
    Tools->>WS: watch_video(workspace_id, url)
    WS->>YT: get_video(url)
    YT-->>WS: video object

    WS->>VR: save_video(workspace_id, video)
    VR->>DB: INSERT video, workspace_video
    DB-->>VR: video_id
    VR-->>WS: video_id = 123

    WS-->>Tools: "Watched video X. Video ID: 123"
    Tools-->>Agent: tool_result

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: get_summary(123)

    Agent->>Tools: execute("get_summary", {video_id: 123})
    Tools->>WS: get_summary(workspace_id, 123)

    WS->>VR: get_video(workspace_id, 123)
    VR->>DB: SELECT video WHERE video_id=123
    DB-->>VR: video dict
    VR-->>WS: video dict

    WS->>SB: summarize(transcript)
    SB-->>WS: summary text

    WS->>VR: save_summary(workspace_id, 123, summary)
    VR->>DB: UPDATE workspace_video SET summary
    DB-->>VR: success

    WS-->>Tools: summary text
    Tools-->>Agent: tool_result

    Agent->>Agent: Claude API call
    Note over Agent: Final response

    Agent-->>WS: AgentResult
    WS-->>API: final_response
    API-->>User: 200 OK with response
```

**Benefits:**
- No in-memory state - load from DB on-demand
- Tools use database video_id (stable across sessions)
- WorkspaceService orchestrates all business logic
- Direct saves (no events needed for simple save operations)
- Scales to any workspace size

**Boundary Analysis (Correct Dependencies):**
- ✓ API → Domain (correct: API depends on Domain)
- ✓ Infrastructure → Domain (correct: VR would implement IVideoRepository from Domain)
- ✓ Domain calls Infrastructure through injected dependencies (WS receives YT, SB, VR via constructor)
- ✓ No Domain → Infrastructure imports (Domain only knows about interfaces)
- ✓ Tools are just functions that delegate to WorkspaceService (thin adapters)
- ✓ All dependencies point inward toward Domain

---

## Streaming Architecture - Event vs Callback Comparison

## Option A: Service Methods Emit Events

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Route
    participant WS as WorkspaceService
    participant Agent as ChatAgent
    participant YT as YouTubeService
    participant VR as VideoRepository
    participant SB as SummaryBot
    participant DB as PostgreSQL
    participant SSE as SSE Stream

    User->>API: POST /messages "Watch and summarize video X"
    API->>WS: send_message(workspace_id, message)

    Note over WS: Create stream handler
    WS->>Agent: chat(message, workspace_id)

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: watch_video(url)

    Agent->>WS: execute_tool("watch_video", url)
    WS->>YT: get_video(url)
    YT-->>WS: video object

    WS->>VR: save_video(workspace_id, video)
    VR->>DB: INSERT video, workspace_video
    DB-->>VR: video_id
    VR-->>WS: video_id

    Note over WS: Emit AgentEvent(video_watched)
    WS->>WS: event_bus.emit(video_watched)
    WS->>SSE: stream("Watched video X, ID: 123")
    SSE-->>User: SSE: "Watched video X"

    WS-->>Agent: tool_result: video_id 123

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: get_summary(123)

    Agent->>WS: execute_tool("get_summary", 123)
    WS->>VR: get_video(workspace_id, 123)
    VR->>DB: SELECT video
    DB-->>VR: video dict
    VR-->>WS: video dict

    WS->>SB: summarize(transcript)
    SB-->>WS: summary text

    WS->>VR: save_summary(workspace_id, 123, summary)
    VR->>DB: UPDATE workspace_video SET summary
    DB-->>VR: success

    Note over WS: Emit AgentEvent(video_summarized)
    WS->>WS: event_bus.emit(video_summarized)
    WS->>SSE: stream("Summary generated")
    SSE-->>User: SSE: "Summary generated"

    WS-->>Agent: tool_result: summary

    Agent->>Agent: Claude API call
    Note over Agent: Final response

    Agent-->>WS: final_response
    WS->>SSE: stream(final_response)
    SSE-->>User: SSE: Final summary text

    WS-->>API: response
    API-->>User: 200 OK (stream complete)
```

**Characteristics:**
- **Event bus pattern** - services emit domain events
- **Decoupled** - service doesn't know about streaming
- **Observers subscribe** - stream handler listens to events
- **More complex** - needs event bus infrastructure
- **Flexible** - multiple listeners can react to same event

---

## Option B: Service Methods Get Stream Callback

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Route
    participant WS as WorkspaceService
    participant Agent as ChatAgent
    participant YT as YouTubeService
    participant VR as VideoRepository
    participant SB as SummaryBot
    participant DB as PostgreSQL
    participant SSE as SSE Stream

    User->>API: POST /messages "Watch and summarize video X"
    API->>WS: send_message(workspace_id, message, stream_callback)

    Note over WS: Pass callback to tools
    WS->>Agent: chat(message, workspace_id, stream_callback)

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: watch_video(url)

    Agent->>WS: watch_video(workspace_id, url, stream_callback)
    WS->>YT: get_video(url)
    YT-->>WS: video object

    WS->>VR: save_video(workspace_id, video)
    VR->>DB: INSERT video, workspace_video
    DB-->>VR: video_id
    VR-->>WS: video_id

    Note over WS: Direct stream call
    WS->>SSE: stream_callback("Watched video X, ID: 123")
    SSE-->>User: SSE: "Watched video X"

    WS-->>Agent: tool_result: video_id 123

    Agent->>Agent: Claude API call
    Note over Agent: Tool use: get_summary(123)

    Agent->>WS: get_summary(workspace_id, 123, stream_callback)
    WS->>VR: get_video(workspace_id, 123)
    VR->>DB: SELECT video
    DB-->>VR: video dict
    VR-->>WS: video dict

    WS->>SB: summarize(transcript)
    SB-->>WS: summary text

    WS->>VR: save_summary(workspace_id, 123, summary)
    VR->>DB: UPDATE workspace_video SET summary
    DB-->>VR: success

    Note over WS: Direct stream call
    WS->>SSE: stream_callback("Summary generated")
    SSE-->>User: SSE: "Summary generated"

    WS-->>Agent: tool_result: summary

    Agent->>Agent: Claude API call
    Note over Agent: Final response

    Agent-->>WS: final_response
    WS->>SSE: stream_callback(final_response)
    SSE-->>User: SSE: Final summary text

    WS-->>API: response
    API-->>User: 200 OK (stream complete)
```

**Characteristics:**
- **Direct callback pattern** - service calls stream function directly
- **Coupled** - service knows about streaming (passed as parameter)
- **Simple** - no event bus needed
- **Explicit** - clear where streaming happens
- **Single listener** - callback is 1:1 with stream

---

## Key Differences

| Aspect | Option A (Events) | Option B (Callback) |
|--------|-------------------|---------------------|
| **Coupling** | Decoupled - service emits, doesn't know who listens | Coupled - service calls callback directly |
| **Infrastructure** | Needs event bus system | Just function parameter |
| **Flexibility** | Multiple listeners possible | Single callback per invocation |
| **Complexity** | Higher - event system to manage | Lower - simple function call |
| **Traceability** | Events can be logged/traced centrally | Callback flow is explicit in code |
| **Testing** | Can test service without stream concerns | Must mock callback in tests |

---

## Recommendation

**For MVP: Option B (Callback)**

**Reasons:**
1. Simpler implementation - no event bus needed
2. Explicit control flow - easy to follow
3. Sufficient for single SSE stream use case
4. Can refactor to event bus later if needed

**When to use Option A:**
- Need multiple listeners (e.g., logging + streaming + metrics)
- Want domain services completely decoupled from infrastructure
- Building event-sourced system
- Need event replay/audit trail

**Implementation Example (Option B):**

```python
# WorkspaceService
def send_message(self, workspace_id, message_text, stream_callback=None):
    def tool_handler(tool_name, args):
        if tool_name == "watch_video":
            return self.watch_video(workspace_id, args['url'], stream_callback)
        elif tool_name == "get_summary":
            return self.get_summary(workspace_id, args['video_id'], stream_callback)

    agent = ChatAgent(workspace_id, tool_handler)
    result = agent.chat(message_text)

    if stream_callback:
        stream_callback(result.final_response)

    return result

def watch_video(self, workspace_id, url, stream_callback=None):
    video = self.youtube_service.get_video(url)
    video_id = self.video_repo.save_video(workspace_id, video.to_dict())

    if stream_callback:
        stream_callback(f"Watched {video.title}. Video ID: {video_id}")

    return video_id

def get_summary(self, workspace_id, video_id, stream_callback=None):
    video = self.video_repo.get_video(workspace_id, video_id)
    summary = self.summary_bot.summarize(video['transcript'])
    self.video_repo.save_summary(workspace_id, video_id, summary)

    if stream_callback:
        stream_callback(f"Summary generated for video {video_id}")

    return summary
```

**Route Handler (FastAPI with SSE):**

```python
@router.post("/messages/stream")
async def send_message_stream(workspace_id: str, message: str):
    async def event_generator():
        def stream_callback(text):
            # Called by WorkspaceService
            yield f"data: {json.dumps({'text': text})}\n\n"

        workspace_service.send_message(workspace_id, message, stream_callback)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```
