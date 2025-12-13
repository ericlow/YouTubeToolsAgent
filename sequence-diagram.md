# Message Flow Sequence Diagram

## Incremental Save Approach (Recommended)

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant Route as messages.py<br/>(Route Handler)
    participant Service as WorkspaceService<br/>(Application Service)
    participant MsgRepo as MessageRepository<br/>(Data Access)
    participant Agent as ChatAgent<br/>(Domain Logic)
    participant DB as PostgreSQL

    Client->>Route: POST /messages<br/>{message: "analyze video X"}

    Route->>Service: send_message(workspace_id, "analyze video X")

    Note over Service: 1. Save user message IMMEDIATELY
    Service->>MsgRepo: save(workspace_id, user_message)
    MsgRepo->>DB: INSERT INTO messages
    DB-->>MsgRepo: ✓ saved
    MsgRepo-->>Service: message saved

    Note over Service: 2. Load conversation history
    Service->>MsgRepo: get_by_workspace(workspace_id)
    MsgRepo->>DB: SELECT * FROM messages WHERE workspace_id=?
    DB-->>MsgRepo: [msg1, msg2, ..., user_message]
    MsgRepo-->>Service: messages list

    Note over Service: 3. Execute agent
    Service->>Agent: new ChatAgent(videos=[], messages)
    Service->>Agent: chat("analyze video X")

    Note over Agent: Agent processes message<br/>with tool loop
    Agent->>Agent: Add user msg to session
    Agent->>Agent: Claude API call
    Agent->>Agent: Tool use (watch_video)
    Agent->>Agent: Tool result (transcript)
    Agent->>Agent: Claude API call
    Agent->>Agent: Final response

    Agent-->>Service: AgentResult(all_messages, final_response)

    Note over Service: 4. Save NEW messages only<br/>(skip user msg - already saved)
    Service->>Service: Extract new messages<br/>(tool_use, tool_result, assistant)
    Service->>MsgRepo: save_batch(workspace_id, new_messages)
    MsgRepo->>DB: INSERT INTO messages (batch)
    DB-->>MsgRepo: ✓ saved
    MsgRepo-->>Service: saved

    Service-->>Route: final_response
    Route-->>Client: 200 OK {response: "..."}
```

## Key Points

1. **User message saved immediately** (line 13-16)
   - Never lost even if agent crashes
   - User sees "received" confirmation instantly

2. **Load includes the message we just saved** (line 19-23)
   - Agent gets full conversation context
   - Includes the user message we just persisted

3. **Agent executes with full context** (line 26-37)
   - Tool loop happens in memory
   - No DB writes during execution

4. **Save only NEW messages** (line 41-47)
   - Skip user message (already saved in step 1)
   - Batch save tool_use, tool_result, assistant messages
   - Atomic - either all save or none

## Failure Scenarios

### Scenario A: Agent crashes mid-execution
```
✅ User message: SAVED (step 1)
❌ Tool messages: LOST
❌ Assistant response: LOST

User can see their message in history and retry.
```

### Scenario B: Database fails during final save
```
✅ User message: SAVED (step 1)
❌ Tool messages: LOST (transaction rollback)
❌ Assistant response: NOT RETURNED to user

User sees error, can retry. Their message is preserved.
```

## Comparison to Batch Approach

### Batch (save everything at end):
- ❌ User message lost if agent crashes
- ✅ All-or-nothing atomicity
- ❌ No visibility during execution

### Incremental (save user message first):
- ✅ User message always saved
- ⚠️ Partial state if agent crashes (user msg exists, no response)
- ✅ Can see user input immediately
- ✅ Better UX - user sees "received" confirmation

