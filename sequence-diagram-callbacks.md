# Message Flow with Callbacks (Real-time Save)

## Callback Approach - Messages Saved During Execution

```mermaid
sequenceDiagram
    participant Client as HTTP Client
    participant Route as messages.py<br/>(Route Handler)
    participant Service as WorkspaceService<br/>(Application Service)
    participant MsgRepo as MessageRepository<br/>(Data Access)
    participant Agent as ChatAgent<br/>(Domain Logic)
    participant Session as ChatSession
    participant DB as PostgreSQL

    Client->>Route: POST /messages<br/>{message: "analyze video X"}
    Route->>Service: send_message(workspace_id, "analyze video X")

    Note over Service: 1. Save user message IMMEDIATELY
    Service->>MsgRepo: save(workspace_id, user_message)
    MsgRepo->>DB: INSERT INTO messages (role=user)
    DB-->>MsgRepo: ✓ saved
    MsgRepo-->>Service: message saved

    Note over Service: 2. Load conversation history
    Service->>MsgRepo: get_by_workspace(workspace_id)
    MsgRepo->>DB: SELECT * FROM messages
    DB-->>MsgRepo: [msg1, msg2, ..., user_message]
    MsgRepo-->>Service: messages list

    Note over Service: 3. Define callback for real-time saves
    Service->>Service: create save_callback(msg)

    Note over Service: 4. Execute agent WITH callback
    Service->>Agent: chat(message, on_message=save_callback)

    rect rgb(220, 240, 255)
        Note over Agent,DB: TOOL LOOP (each message saved immediately)

        Agent->>Session: send(user_message)
        Session->>Session: messages.append(user_msg)
        Session->>Session: Claude API call

        Note over Session: Claude responds with tool_use
        Session->>Session: messages.append(assistant_tool_use)
        Session->>Agent: response (stop_reason=tool_use)

        Agent->>Service: callback(assistant_tool_use_msg)
        Service->>MsgRepo: save(workspace_id, tool_use_msg)
        MsgRepo->>DB: INSERT (role=assistant, tool_use)
        DB-->>MsgRepo: ✓ saved

        Agent->>Agent: execute_tool(watch_video)
        Agent->>Agent: tool returns transcript

        Agent->>Session: send(tool_result_message)
        Session->>Session: messages.append(tool_result)

        Agent->>Service: callback(tool_result_msg)
        Service->>MsgRepo: save(workspace_id, tool_result_msg)
        MsgRepo->>DB: INSERT (role=user, tool_result)
        DB-->>MsgRepo: ✓ saved

        Session->>Session: Claude API call

        Note over Session: Claude responds with final text
        Session->>Session: messages.append(assistant_text)
        Session->>Agent: response (stop_reason=end_turn)

        Agent->>Service: callback(assistant_final_msg)
        Service->>MsgRepo: save(workspace_id, final_msg)
        MsgRepo->>DB: INSERT (role=assistant, text)
        DB-->>MsgRepo: ✓ saved
    end

    Agent-->>Service: AgentResult(all_messages, final_response)

    Note over Service: No batch save needed<br/>(everything already saved via callbacks)

    Service-->>Route: final_response
    Route-->>Client: 200 OK {response: "..."}
```

## Key Differences from Batch Approach

### Messages Saved During Execution (Real-time)

1. **User message** → Saved BEFORE agent starts
2. **Tool use message** → Saved IMMEDIATELY when created (during tool loop)
3. **Tool result message** → Saved IMMEDIATELY when created (during tool loop)
4. **Final assistant message** → Saved IMMEDIATELY when created (during tool loop)

### Benefits

✅ **Database always current** - Can query DB mid-execution to see progress
✅ **Never lose tool messages** - Saved as they happen, not batched
✅ **Streaming-ready** - Callback is same mechanism needed for streaming
✅ **Better debugging** - See exact state even if agent crashes mid-loop

### Implementation Changes Required

**ChatAgent needs callback parameter:**
```python
def chat(self, message: str, on_message: callable = None) -> AgentResult:
    # ... existing code ...

    while True:
        if response.stop_reason != 'tool_use':
            # Final message
            if on_message:
                on_message(final_message)
            break
        else:
            # Tool use message
            tool_use_msg = {...}
            if on_message:
                on_message(tool_use_msg)

            # Execute tool
            tool_result_msg = {...}
            if on_message:
                on_message(tool_result_msg)
```

**WorkspaceService creates callback:**
```python
def send_message(self, workspace_id: int, message_text: str) -> str:
    # Save user message
    self.message_repo.save(workspace_id, user_message)

    # Load history
    messages = self.message_repo.get_by_workspace(workspace_id)

    # Define callback
    def save_callback(message):
        self.message_repo.save(workspace_id, message)

    # Execute with callback
    agent = ChatAgent(videos=[], messages=messages)
    result = agent.chat(message_text, on_message=save_callback)

    return result.final_response
```

## Future: Streaming Extension

When adding streaming, just extend the callback:

```python
def send_message_stream(self, workspace_id, message_text):
    # Same setup...

    def stream_and_save_callback(message):
        self.message_repo.save(workspace_id, message)  # Save (already doing this)
        yield format_sse(message)  # AND stream to client (new)

    for event in agent.chat_stream(message_text, on_message=stream_and_save_callback):
        yield event
```

**The callback mechanism is the foundation for streaming.**

