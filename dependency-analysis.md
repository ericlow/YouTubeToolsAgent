# Dependency Analysis - Import Structure

This document shows **compile-time dependencies** (what imports what), not runtime behavior.

---

## 1. Component/Dependency Diagram

### Current Architecture - Import Dependencies

```mermaid
graph TB
    subgraph "API Layer"
        Routes[api/routes/messages.py]
    end

    subgraph "Domain Layer"
        WS[domain/services/workspace_service.py]
        Agent[components/agents/chat_agent.py]
        TE[components/tool_executor.py]
        ChatApp[components/services/chat_appllcation.py]
    end

    subgraph "Infrastructure Layer"
        VR[domain/repositories/video_repository.py]
        YT[components/services/youtube_service.py]
        SB[components/services/youtube_summary_bot.py]
        DB[infrastructure/orm_database.py]
        VideoModel[api/models/video_model.py]
    end

    %% API Layer imports
    Routes -->|imports WorkspaceService| WS

    %% Domain Layer imports
    WS -->|imports ChatAgent| Agent
    WS -->|imports VideoRepository| VR
    Agent -->|imports ToolExecutor| TE
    Agent -->|imports ChatApplication| ChatApp
    TE -->|imports ChatApplication| ChatApp

    %% VIOLATIONS: Domain imports Infrastructure
    ChatApp -->|VIOLATION: imports YouTubeService| YT
    ChatApp -->|VIOLATION: imports YouTubeSummaryBot| SB
    VR -->|VIOLATION: imports VideoModel| VideoModel
    VR -->|VIOLATION: imports get_session| DB

    %% Infrastructure imports
    VideoModel -->|imports| DB

    %% Styling
    style ChatApp fill:#ffcccc
    style YT fill:#ffffcc
    style SB fill:#ffffcc
    style VR fill:#ffcccc
```

**Violations (red boxes):**
- `chat_appllcation.py` imports `youtube_service.py` (Domain → Infrastructure)
- `chat_appllcation.py` imports `youtube_summary_bot.py` (Domain → Infrastructure)
- `video_repository.py` imports `video_model.py` (Domain → Infrastructure - wrong layer)
- `video_repository.py` imports `orm_database.py` (Domain → Infrastructure)

**These are COMPILE-TIME dependencies - the imports in the code.**

---

### DDD Architecture - Import Dependencies (Corrected)

```mermaid
graph TB
    subgraph "API Layer"
        Routes[api/routes/messages.py]
    end

    subgraph "Domain Layer"
        WS[domain/services/workspace_service.py]
        Agent[components/agents/chat_agent.py]
        Tools[Tool Handler function]
        IVideoRepo[domain/repositories/video_repository_interface.py]
        IYouTube[domain/services/youtube_service_interface.py]
        ISummary[domain/services/summary_bot_interface.py]
    end

    subgraph "Infrastructure Layer"
        VR[infrastructure/repositories/video_repository.py]
        YT[infrastructure/services/youtube_service.py]
        SB[infrastructure/services/summary_bot.py]
        DB[infrastructure/orm_database.py]
        VideoModel[infrastructure/models/video_model.py]
    end

    %% API Layer imports - API can import from both Domain and Infrastructure
    Routes -->|imports WorkspaceService| WS
    Routes -->|imports PostgreSQLVideoRepository| VR
    Routes -->|imports YouTubeService| YT
    Routes -->|imports SummaryBot| SB

    %% Domain Layer imports - ONLY from Domain
    WS -->|imports IVideoRepository interface| IVideoRepo
    WS -->|imports IYouTubeService interface| IYouTube
    WS -->|imports ISummaryBot interface| ISummary
    WS -->|imports ChatAgent| Agent
    Agent -->|imports Tools| Tools

    %% Infrastructure imports from Domain (DEPENDENCY INVERSION)
    VR -->|implements IVideoRepository| IVideoRepo
    YT -->|implements IYouTubeService| IYouTube
    SB -->|implements ISummaryBot| ISummary

    %% Infrastructure imports within Infrastructure
    VR -->|imports VideoModel| VideoModel
    VR -->|imports get_session| DB
    VideoModel -->|imports| DB

    %% Styling
    style IVideoRepo fill:#ccffcc
    style IYouTube fill:#ccffcc
    style ISummary fill:#ccffcc
    style WS fill:#ccffcc
```

**All dependencies point INWARD toward Domain (green boxes = interfaces):**
- Domain only imports Domain interfaces
- Infrastructure imports and implements Domain interfaces
- API wires everything together (can import from both layers)

**No violations - all arrows either stay within layer or point toward Domain.**

---

## 3. Layer Diagram with Import Arrows

### Current Architecture - Layer Dependencies

```mermaid
graph LR
    subgraph External
        User((User))
        PostgreSQL[(PostgreSQL)]
        YouTube[YouTube API]
        Claude[Claude API]
    end

    subgraph API["API LAYER<br/>api/routes/"]
        Routes[messages.py]
    end

    subgraph Domain["DOMAIN LAYER<br/>domain/services/<br/>components/agents/"]
        WS[WorkspaceService]
        Agent[ChatAgent]
        ChatApp[ChatApplication]
    end

    subgraph Infra["INFRASTRUCTURE LAYER<br/>infrastructure/<br/>components/services/"]
        VR[VideoRepository]
        YT[YouTubeService]
        SB[SummaryBot]
        DB[ORM Database]
    end

    %% User interaction
    User -->|HTTP| Routes

    %% Correct dependencies (API → Domain)
    Routes -->|imports| WS

    %% Correct dependencies (Domain → Domain)
    WS -->|imports| Agent
    Agent -->|imports| ChatApp

    %% WRONG: Domain → Infrastructure (VIOLATION)
    WS -->|imports| VR
    ChatApp -->|imports| YT
    ChatApp -->|imports| SB
    VR -->|imports| DB

    %% Infrastructure → External
    DB -->|connects to| PostgreSQL
    YT -->|calls| YouTube
    Agent -->|calls| Claude

    %% Styling
    style API fill:#cce5ff
    style Domain fill:#ffe6cc
    style Infra fill:#ffcccc
    linkStyle 5,6,7,8 stroke:#ff0000,stroke-width:3px
```

**Red arrows = VIOLATIONS (Domain importing from Infrastructure)**

---

### DDD Architecture - Layer Dependencies (Corrected)

```mermaid
graph LR
    subgraph External
        User((User))
        PostgreSQL[(PostgreSQL)]
        YouTube[YouTube API]
        Claude[Claude API]
    end

    subgraph API["API LAYER<br/>api/routes/"]
        Routes[messages.py]
    end

    subgraph Domain["DOMAIN LAYER<br/>domain/services/<br/>domain/repositories/"]
        WS[WorkspaceService]
        Agent[ChatAgent]
        IVideoRepo[IVideoRepository<br/>interface]
        IYouTube[IYouTubeService<br/>interface]
        ISummary[ISummaryBot<br/>interface]
    end

    subgraph Infra["INFRASTRUCTURE LAYER<br/>infrastructure/repositories/<br/>infrastructure/services/"]
        VR[PostgreSQLVideoRepository<br/>implements]
        YT[YouTubeService<br/>implements]
        SB[SummaryBot<br/>implements]
        DB[ORM Database]
    end

    %% User interaction
    User -->|HTTP| Routes

    %% API wires everything together
    Routes -->|imports| WS
    Routes -->|creates and injects| VR
    Routes -->|creates and injects| YT
    Routes -->|creates and injects| SB

    %% Domain → Domain (correct)
    WS -->|imports| Agent
    WS -->|imports| IVideoRepo
    WS -->|imports| IYouTube
    WS -->|imports| ISummary

    %% Infrastructure → Domain (DEPENDENCY INVERSION - correct)
    VR -->|implements| IVideoRepo
    YT -->|implements| IYouTube
    SB -->|implements| ISummary

    %% Infrastructure → Infrastructure
    VR -->|imports| DB

    %% Infrastructure → External
    DB -->|connects to| PostgreSQL
    YT -->|calls| YouTube
    Agent -->|calls| Claude

    %% Styling
    style API fill:#cce5ff
    style Domain fill:#ccffcc
    style Infra fill:#fff4cc
    style IVideoRepo fill:#90EE90
    style IYouTube fill:#90EE90
    style ISummary fill:#90EE90
```

**Green = Correct dependencies (all pointing toward Domain interfaces)**

**Key difference:**
- **Current:** Domain imports Infrastructure (red arrows going right)
- **DDD:** Infrastructure imports Domain interfaces (arrows going left toward center)

---

## Code Examples - Side by Side

### Current Architecture (WRONG)

```python
# components/services/chat_appllcation.py (DOMAIN LAYER)
from components.services.youtube_summary_bot import YouTubeSummaryBot  # ← VIOLATION
from components.services.youtube_service import YouTubeService  # ← VIOLATION

class ChatApplication:
    def __init__(self, videos: list[YouTubeVideo] = [], on_event: Callable=None):
        self.youtube: YouTubeService = YouTubeService()  # ← Creates Infrastructure
        self.summary_bot = YouTubeSummaryBot()  # ← Creates Infrastructure
        self.videos = videos
        self.on_event = on_event
```

**Problem:** Domain layer imports and creates Infrastructure classes directly.

---

### DDD Architecture (CORRECT)

```python
# domain/services/workspace_service.py (DOMAIN LAYER)
from domain.repositories.video_repository_interface import IVideoRepository  # ← Domain interface
from domain.services.youtube_service_interface import IYouTubeService  # ← Domain interface
from domain.services.summary_bot_interface import ISummaryBot  # ← Domain interface

class WorkspaceService:
    def __init__(
        self,
        video_repo: IVideoRepository,  # ← Injected interface
        youtube_service: IYouTubeService,  # ← Injected interface
        summary_bot: ISummaryBot  # ← Injected interface
    ):
        self.video_repo = video_repo
        self.youtube = youtube_service
        self.summary_bot = summary_bot

    def watch_video(self, workspace_id, url):
        video = self.youtube.get_video(url)  # Uses interface, doesn't know concrete class
        video_id = self.video_repo.save(workspace_id, video.to_dict())
        return video_id
```

```python
# infrastructure/services/youtube_service.py (INFRASTRUCTURE LAYER)
from domain.services.youtube_service_interface import IYouTubeService  # ← Imports from Domain

class YouTubeService(IYouTubeService):  # ← Implements Domain interface
    def get_video(self, url):
        # YouTube API specific implementation
        pass
```

```python
# api/routes/messages.py (API LAYER - wires everything together)
from domain.services.workspace_service import WorkspaceService
from infrastructure.repositories.video_repository import PostgreSQLVideoRepository
from infrastructure.services.youtube_service import YouTubeService
from infrastructure.services.summary_bot import SummaryBot

@router.post("/messages")
def send_message(workspace_id: str, message: str):
    # API layer creates concrete implementations
    video_repo = PostgreSQLVideoRepository(get_session())
    youtube_service = YouTubeService()
    summary_bot = SummaryBot()

    # API layer injects them into domain service
    workspace_service = WorkspaceService(
        video_repo=video_repo,
        youtube_service=youtube_service,
        summary_bot=summary_bot
    )

    result = workspace_service.send_message(workspace_id, message)
    return result
```

**Solution:**
- Domain only imports interfaces (from Domain layer)
- Infrastructure implements interfaces (imports FROM Domain)
- API wires concrete implementations into domain services (dependency injection)

---

## Summary

**The diagrams show:**

1. **Component/Dependency Diagram:** Shows which files import which (compile-time structure)
2. **Layer Diagram:** Shows dependency direction between layers

**Current Architecture violations:**
- Red arrows going FROM Domain TO Infrastructure
- Domain creates Infrastructure objects with `new`
- Domain imports from Infrastructure layer

**DDD Architecture (correct):**
- Green arrows going FROM Infrastructure TO Domain
- Domain only knows about interfaces
- Infrastructure implements Domain interfaces
- API does all the wiring (dependency injection)

**This is the difference that sequence diagrams don't show - the import/dependency structure, not the runtime behavior.**
