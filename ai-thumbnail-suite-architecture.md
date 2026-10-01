# AI Thumbnail Suite --- Product & Technical Architecture

## 1. Product Overview

AI Thumbnail Suite is a multi-agent AI application that turns a
creator's video idea into high-quality YouTube thumbnails.

A user can provide:

-   A natural-language description of the video
-   An optional YouTube video URL
-   Optional example/reference thumbnails
-   Optional creator photos
-   Optional brand assets and style preferences

The system analyzes the content and references, develops multiple
thumbnail concepts, generates visual designs, critiques them, iterates,
and returns final thumbnails.

### Core product promise

> **Describe your video, show us the style you like, and let an AI
> thumbnail team create the thumbnail.**

------------------------------------------------------------------------

# 2. Core User Workflow

``` text
User
 │
 ├── Video description
 ├── YouTube URL (optional)
 ├── Reference thumbnails (optional)
 ├── Creator photo (optional)
 └── Brand assets (optional)
 │
 ▼
Project Creation
 │
 ▼
Multi-Agent Analysis
 │
 ├── Video Analyst
 ├── Reference Analyst
 ├── Audience Analyst
 └── Content/Visual Research
 │
 ▼
Thumbnail Strategy
 │
 ├── Hook Strategist
 ├── Concept Generator
 └── Creative Director
 │
 ▼
Visual Design
 │
 └── Visual Director
 │
 ▼
Image Generation
 │
 └── Image Generation Provider
 │
 ▼
Quality Control
 │
 ├── Thumbnail Critic
 ├── Mobile Readability Check
 └── Reference Consistency Check
 │
 ▼
Revision Loop
 │
 ▼
Final Thumbnails
 │
 ├── Edit
 ├── Regenerate
 ├── Create Variations
 └── Export
```

------------------------------------------------------------------------

# 3. Key Features

## 3.1 Video Input

Users can describe their video in natural language.

Example:

> I tested 20 AI coding tools to see which one can actually replace a
> developer.

The system should extract:

-   Main topic
-   Core story
-   Main subject
-   Conflict/tension
-   Emotional angle
-   Important entities
-   Potential visual metaphors
-   Potential thumbnail hooks
-   Audience
-   Category

------------------------------------------------------------------------

## 3.2 YouTube URL Input

Users can paste a YouTube URL.

The system can extract, where technically and legally available:

-   Video title
-   Description
-   Channel information
-   Thumbnail
-   Metadata
-   Relevant public content/context

The URL should become another input signal rather than the sole source
of truth.

### Pipeline

``` text
YouTube URL
    │
    ▼
URL Validator
    │
    ▼
Metadata Fetcher
    │
    ▼
Content Extractor
    │
    ▼
Video Understanding
    │
    ▼
Thumbnail Strategy
```

------------------------------------------------------------------------

# 4. Reference Thumbnail System

Users can upload one or multiple example thumbnails.

The Reference Analyst should identify:

### Composition

-   Subject position
-   Text position
-   Image balance
-   Negative space
-   Foreground/background separation
-   Visual hierarchy
-   Camera framing

### Typography

-   Approximate text size
-   Text density
-   Placement
-   Number of words
-   Contrast
-   Alignment

### Color

-   Dominant palette
-   Accent colors
-   Contrast
-   Saturation
-   Background treatment

### Visual Style

-   Photorealistic
-   Cinematic
-   Graphic
-   Minimal
-   Meme-style
-   Editorial
-   Dramatic
-   Technical
-   Gaming
-   Educational
-   etc.

### Important principle

The system should extract a **style profile**, not simply copy the
reference.

``` json
{
  "composition": {
    "subject_position": "right",
    "text_position": "left",
    "subject_scale": "large"
  },
  "typography": {
    "word_count": "2-5",
    "weight": "heavy",
    "contrast": "high"
  },
  "color": {
    "contrast": "high",
    "saturation": "high"
  },
  "visual_style": "dramatic cinematic"
}
```

------------------------------------------------------------------------

# 5. Multi-Agent Architecture

The application should use specialized agents instead of one large
prompt.

## 5.1 Orchestrator Agent

The Orchestrator owns the workflow.

Responsibilities:

-   Create project state
-   Decide which agents should run
-   Pass structured outputs between agents
-   Select models
-   Handle failures
-   Trigger revision loops
-   Track generation attempts
-   Decide when the result is ready

The Orchestrator should not perform every task itself.

------------------------------------------------------------------------

## 5.2 Video Analyst Agent

Responsibilities:

-   Understand the video
-   Extract the central idea
-   Identify tension/conflict
-   Identify important subjects
-   Identify possible visual concepts
-   Create a structured video brief

Output:

``` json
{
  "topic": "...",
  "core_story": "...",
  "central_tension": "...",
  "key_entities": [],
  "audience": "...",
  "emotional_angles": [],
  "visual_opportunities": []
}
```

------------------------------------------------------------------------

## 5.3 Reference Analyst Agent

Responsibilities:

-   Analyze uploaded thumbnails
-   Extract composition patterns
-   Analyze typography
-   Analyze colors
-   Analyze visual language
-   Identify reusable design characteristics

Output:

``` json
{
  "style_summary": "...",
  "composition": {},
  "typography": {},
  "color_palette": [],
  "visual_language": [],
  "do_not_copy": []
}
```

------------------------------------------------------------------------

## 5.4 Audience Analyst Agent

Responsibilities:

-   Identify likely viewer
-   Understand viewer motivations
-   Identify curiosity triggers
-   Identify relevant emotional angles
-   Help determine the visual promise

Output:

``` json
{
  "audience": "...",
  "viewer_intent": [],
  "curiosity_triggers": [],
  "emotional_angles": []
}
```

------------------------------------------------------------------------

## 5.5 Hook Strategist Agent

Generates multiple thumbnail hooks.

Example:

``` text
AI WON.

20 → 1

GOODBYE DEVELOPERS

THIS ONE WINS

AI CAN CODE?
```

The agent should produce different creative angles rather than simple
wording variations.

------------------------------------------------------------------------

## 5.6 Concept Generator Agent

Creates several distinct thumbnail concepts.

Example:

### Concept A --- AI vs Developer

A surprised developer looks at an AI-generated coding interface.

### Concept B --- 20 Tools → 1 Winner

Twenty tools appear in the background while one winner dominates the
foreground.

### Concept C --- Developer Replacement

An AI system occupies the developer's workspace while the developer
reacts.

Each concept should contain:

-   Concept name
-   Hook
-   Visual story
-   Subject
-   Background
-   Composition
-   Text
-   Emotional direction
-   Why it works

------------------------------------------------------------------------

## 5.7 Creative Director Agent

Selects and refines concepts.

Inputs:

-   Video brief
-   Audience profile
-   Reference profile
-   Hook candidates
-   Generated concepts

Outputs a final creative direction.

------------------------------------------------------------------------

## 5.8 Visual Director Agent

Transforms the creative direction into a detailed visual specification.

Example:

``` json
{
  "canvas": "1280x720",
  "subject": {
    "position": "right",
    "scale": "large",
    "expression": "surprised"
  },
  "background": {
    "description": "...",
    "depth": "medium"
  },
  "lighting": "...",
  "composition": "...",
  "text": {
    "content": "AI WON.",
    "position": "left",
    "size": "very large"
  }
}
```

------------------------------------------------------------------------

## 5.9 Image Generation Agent

Responsible for image generation.

It should support multiple providers.

Potential providers:

-   OpenAI image generation
-   Google image models
-   Stability/other image APIs
-   Self-hosted image models
-   ComfyUI
-   Other compatible providers

The image generation layer should be provider-agnostic.

------------------------------------------------------------------------

## 5.10 Thumbnail Critic Agent

Evaluates generated thumbnails.

Evaluation dimensions:

-   Subject clarity
-   Visual hierarchy
-   Mobile readability
-   Hook strength
-   Contrast
-   Composition
-   Emotional impact
-   Reference adherence
-   Brand consistency
-   Text readability
-   Unnecessary visual clutter

Example:

``` json
{
  "overall": 82,
  "issues": [
    {
      "type": "text_readability",
      "severity": "medium",
      "message": "Headline loses contrast on the background."
    }
  ],
  "recommended_changes": [
    "Increase headline contrast",
    "Reduce background detail"
  ]
}
```

The score is primarily an internal QA mechanism, not necessarily
something shown to users as a definitive prediction of performance.

------------------------------------------------------------------------

# 6. Revision Loop

The system should support iterative generation.

``` text
Generate
   │
   ▼
Critic
   │
   ├── Good ───────────► Final
   │
   └── Needs revision
             │
             ▼
       Visual Director
             │
             ▼
       Image Generator
             │
             └────────► Critic
```

Limit automatic iterations to avoid runaway cost.

Suggested default:

-   Maximum 2--3 automatic revisions
-   User can manually request more

------------------------------------------------------------------------

# 7. Model Architecture

A major requirement is support for both **local LLMs and frontier
LLMs**.

Do not hard-code model providers into agents.

Instead use a common model abstraction.

``` text
                    Model Router
                        │
          ┌─────────────┼─────────────┐
          │             │             │
       Local         Frontier       Vision
       Models         Models        Models
          │             │             │
      Ollama          OpenAI       Vision APIs
      vLLM            Anthropic
      llama.cpp       Google
      LM Studio       Other APIs
```

------------------------------------------------------------------------

# 8. Model Provider Abstraction

Python interface:

``` python
class LLMProvider(Protocol):

    async def generate(
        self,
        request: LLMRequest
    ) -> LLMResponse:
        ...

    def supports(
        self,
        capability: Capability
    ) -> bool:
        ...

    def estimate_cost(
        self,
        request: LLMRequest
    ) -> float:
        ...
```

Every provider implements the same interface.

------------------------------------------------------------------------

# 9. Local Model Support

Support:

-   Ollama
-   vLLM
-   llama.cpp
-   LM Studio
-   OpenAI-compatible local endpoints

Example configuration:

``` yaml
providers:
  local:
    type: ollama
    endpoint: http://localhost:11434
    model: <configured-model>
```

Local-first users should be able to keep as much processing local as
possible.

------------------------------------------------------------------------

# 10. Frontier Model Support

The system should support multiple cloud providers through adapters.

Examples:

-   OpenAI
-   Anthropic
-   Google
-   Other compatible providers

Example:

``` yaml
providers:
  frontier:
    - provider: openai
      model: <configured-model>

    - provider: anthropic
      model: <configured-model>

    - provider: google
      model: <configured-model>
```

Do not make the rest of the application depend on any one vendor.

------------------------------------------------------------------------

# 11. Model Router

The Model Router chooses a model based on:

-   Required capability
-   User preference
-   Quality
-   Latency
-   Cost
-   Context length
-   Vision support
-   Tool-calling support
-   Structured-output support
-   Availability

Modes:

``` text
Auto
Local-first
Frontier-first
Maximum quality
Cost optimized
Custom
```

Example:

  Agent               Typical Model Strategy
  ------------------- ------------------------
  Video Analyst       Local / Auto
  Audience Analyst    Local / Auto
  Reference Analyst   Vision-capable
  Hook Strategist     Local or Frontier
  Concept Generator   Frontier
  Creative Director   Frontier
  Visual Director     Frontier
  Critic              Vision-capable
  Simple formatting   Local

These are defaults, not hard requirements.

------------------------------------------------------------------------

# 12. Agent Runtime

Each agent should have:

``` python
class Agent:

    name: str
    capabilities: list[str]

    async def run(
        self,
        state: ProjectState,
        context: AgentContext
    ) -> AgentResult:
        ...
```

Agents should be stateless where possible.

Persistent information belongs in Project State and storage.

------------------------------------------------------------------------

# 13. Shared Project State

Use a structured project state rather than passing large text prompts
between agents.

``` python
class ProjectState:
    project_id: str

    video_brief: VideoBrief
    audience_profile: AudienceProfile
    reference_profile: ReferenceProfile

    hooks: list[Hook]
    concepts: list[ThumbnailConcept]

    selected_concept: ThumbnailConcept | None
    design_spec: DesignSpec | None

    generations: list[Generation]
    critiques: list[Critique]

    final_asset: Asset | None
```

This makes the workflow:

-   Debuggable
-   Resumable
-   Observable
-   Reproducible
-   Easier to modify

------------------------------------------------------------------------

# 14. React Frontend

Use React + TypeScript.

Recommended stack:

-   React
-   TypeScript
-   Vite
-   Tailwind CSS
-   shadcn/ui
-   TanStack Query
-   Zustand
-   React Router
-   React Hook Form
-   Zod
-   Framer Motion
-   Fabric.js or Konva for the thumbnail editor

------------------------------------------------------------------------

# 15. Frontend Screens

## Dashboard

Show:

-   Projects
-   Recent thumbnails
-   Drafts
-   Favorites
-   Usage
-   Create project

------------------------------------------------------------------------

## Create Project

Main input:

``` text
Describe your video

[........................................]

Add references

[ Upload thumbnails ]

or

[ Paste YouTube URL ]

Optional:
[ Upload creator photo ]
[ Upload brand assets ]

              Generate
```

------------------------------------------------------------------------

## Agent Progress

Show the workflow visually:

``` text
✓ Understanding video
✓ Studying references
✓ Identifying audience
✓ Developing hooks
● Creating concepts
○ Generating images
○ Quality review
```

------------------------------------------------------------------------

## Concept Selection

Show 3--6 concepts.

Each card:

-   Preview
-   Hook
-   Concept description
-   Visual reasoning
-   Generate button

------------------------------------------------------------------------

## Thumbnail Workspace

Editor features:

-   Preview
-   Text editing
-   Positioning
-   Scaling
-   Image replacement
-   Background replacement
-   Crop
-   Layers
-   Brand elements
-   Regenerate selected element
-   Generate variations

------------------------------------------------------------------------

## Variations

Allow:

``` text
Generate 4 variations

[ More dramatic ]
[ More minimal ]
[ Bigger face ]
[ Different hook ]
[ Keep style, change concept ]
```

------------------------------------------------------------------------

## Export

Support:

-   PNG
-   JPG
-   WebP
-   1280×720
-   Custom dimensions

------------------------------------------------------------------------

# 16. Python Backend

Recommended:

-   Python 3.12+
-   FastAPI
-   Pydantic v2
-   SQLAlchemy
-   PostgreSQL
-   Redis
-   Celery or Dramatiq
-   S3-compatible object storage
-   WebSockets or Server-Sent Events

------------------------------------------------------------------------

# 17. Backend Architecture

``` text
React
  │
  │ HTTPS / WebSocket
  ▼
FastAPI
  │
  ├── Auth Service
  ├── Project Service
  ├── Asset Service
  ├── Agent Service
  ├── Model Router
  ├── Generation Service
  ├── Thumbnail Service
  └── Export Service
  │
  ├───────────────┐
  ▼               ▼
PostgreSQL       Redis
                    │
                    ▼
              Worker System
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Agents   Image Jobs  Analysis
```

------------------------------------------------------------------------

# 18. Async Job Architecture

AI generation can take seconds or minutes.

Do not make the main HTTP request wait for the entire workflow.

Use asynchronous jobs.

``` text
POST /projects/{id}/generate
          │
          ▼
       Create Job
          │
          ▼
        Queue
          │
          ▼
        Worker
          │
          ▼
    Agent Workflow
          │
          ▼
      Job Events
          │
          ▼
 React WebSocket/SSE
```

------------------------------------------------------------------------

# 19. Real-Time Agent Events

Frontend should receive events such as:

``` json
{
  "type": "agent_started",
  "agent": "reference_analyst"
}
```

``` json
{
  "type": "agent_completed",
  "agent": "reference_analyst"
}
```

``` json
{
  "type": "generation_completed",
  "generation_id": "..."
}
```

This powers the live AI workflow UI.

------------------------------------------------------------------------

# 20. Database

Use PostgreSQL.

Core tables:

``` text
users
projects
project_inputs
assets
reference_images
video_sources
agent_runs
agent_outputs
thumbnail_concepts
design_specs
generations
critiques
exports
model_providers
model_configs
usage_records
```

------------------------------------------------------------------------

# 21. Suggested Relationships

``` text
User
 │
 └── Projects
       │
       ├── Inputs
       ├── References
       ├── Agent Runs
       ├── Concepts
       ├── Generations
       ├── Critiques
       └── Exports
```

------------------------------------------------------------------------

# 22. Object Storage

Use S3-compatible storage.

Options:

-   AWS S3
-   Cloudflare R2
-   MinIO for self-hosted deployments

Store:

-   Uploaded thumbnails
-   Creator images
-   Generated images
-   Final thumbnails
-   Export files
-   Intermediate assets

Never store large image blobs directly in PostgreSQL.

------------------------------------------------------------------------

# 23. Vector Database

A vector database is optional initially.

Potential future uses:

-   User's previous thumbnail styles
-   Brand style retrieval
-   Reference similarity
-   Personal creative memory
-   Template retrieval

Possible technologies:

-   pgvector
-   Qdrant
-   Weaviate

For MVP, PostgreSQL + pgvector is sufficient.

------------------------------------------------------------------------

# 24. Thumbnail Editor

Use a browser canvas layer.

Recommended:

-   Fabric.js
-   Konva
-   HTML Canvas

Editor should represent:

``` text
Canvas
 ├── Background
 ├── Main Subject
 ├── Secondary Objects
 ├── Text
 ├── Logos
 ├── Effects
 └── Overlays
```

Keep the generated image and editable overlay layers separate when
possible.

------------------------------------------------------------------------

# 25. Text Rendering Strategy

Do not depend entirely on an image model for typography.

Recommended pipeline:

``` text
AI creates visual scene
        │
        ▼
Image generation
        │
        ▼
Composition engine
        │
        ├── Headline
        ├── Logo
        ├── Brand elements
        └── Effects
        │
        ▼
Final thumbnail
```

This gives reliable:

-   Text spelling
-   Font control
-   Positioning
-   Branding
-   Editing
-   Variations

------------------------------------------------------------------------

# 26. AI Prompt Architecture

Avoid giant prompts.

Use layered prompts.

``` text
System instructions
        +
Agent role
        +
Project state
        +
Reference profile
        +
Current task
        +
Output schema
```

Require structured outputs wherever possible.

Use Pydantic models for validation.

------------------------------------------------------------------------

# 27. Tool Architecture

Agents should access tools through a common tool registry.

Possible tools:

``` text
youtube_metadata
image_analysis
image_search
asset_storage
image_generation
image_editing
thumbnail_render
brand_lookup
project_state
web_research
```

Each tool should have:

-   Name
-   Description
-   JSON schema
-   Permission
-   Timeout
-   Cost metadata

------------------------------------------------------------------------

# 28. Observability

This is critical for a multi-agent application.

Track:

-   Agent execution time
-   Model used
-   Input tokens
-   Output tokens
-   Estimated cost
-   Tool calls
-   Errors
-   Retries
-   Generation latency
-   Critic results
-   Revision count

Recommended tools:

-   OpenTelemetry
-   Prometheus
-   Grafana
-   Sentry
-   Langfuse

Langfuse is particularly useful for LLM traces and prompt/version
tracking.

------------------------------------------------------------------------

# 29. Prompt Management

Store prompts as versioned files.

``` text
prompts/
  video_analyst/
    v1.md
    v2.md

  reference_analyst/
    v1.md

  creative_director/
    v1.md

  critic/
    v1.md
```

Never bury production prompts directly inside Python code.

Track:

-   Prompt version
-   Model
-   Agent version
-   Project
-   Result quality

------------------------------------------------------------------------

# 30. Security

Implement:

-   Authentication
-   Authorization
-   Project-level access control
-   Signed asset URLs
-   Upload size limits
-   MIME validation
-   Malware scanning for uploads
-   Rate limiting
-   API key encryption
-   Provider credential isolation
-   Job ownership validation

Never expose provider API keys to React.

------------------------------------------------------------------------

# 31. Privacy

Give users explicit control over model routing.

Example:

``` text
Privacy Mode

○ Cloud AI allowed
○ Local models only
○ Hybrid
```

If local-only mode is selected:

-   Do not send prompts to cloud LLMs
-   Do not send images to cloud vision providers
-   Do not send user assets to cloud image services

The application should clearly show when external providers are being
used.

------------------------------------------------------------------------

# 32. API Design

Example REST API:

``` text
POST   /api/projects
GET    /api/projects
GET    /api/projects/{id}
DELETE /api/projects/{id}

POST   /api/projects/{id}/inputs
POST   /api/projects/{id}/references
POST   /api/projects/{id}/generate

GET    /api/projects/{id}/concepts
POST   /api/projects/{id}/concepts/{concept_id}/generate

GET    /api/projects/{id}/generations
POST   /api/projects/{id}/generations/{id}/critique
POST   /api/projects/{id}/generations/{id}/revise

POST   /api/projects/{id}/variations
POST   /api/projects/{id}/export
```

Realtime:

``` text
/ws/projects/{project_id}
```

------------------------------------------------------------------------

# 33. Suggested Python Project Structure

``` text
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── projects.py
│   │   ├── assets.py
│   │   ├── generations.py
│   │   └── exports.py
│   │
│   ├── agents/
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── video_analyst.py
│   │   ├── reference_analyst.py
│   │   ├── audience_analyst.py
│   │   ├── hook_strategist.py
│   │   ├── concept_generator.py
│   │   ├── creative_director.py
│   │   ├── visual_director.py
│   │   └── critic.py
│   │
│   ├── models/
│   │   ├── project.py
│   │   ├── asset.py
│   │   ├── generation.py
│   │   └── agent_run.py
│   │
│   ├── providers/
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── google.py
│   │   ├── ollama.py
│   │   ├── vllm.py
│   │   └── router.py
│   │
│   ├── tools/
│   │   ├── youtube.py
│   │   ├── image_analysis.py
│   │   ├── image_generation.py
│   │   └── storage.py
│   │
│   ├── services/
│   │   ├── project_service.py
│   │   ├── generation_service.py
│   │   └── export_service.py
│   │
│   ├── workers/
│   │   └── tasks.py
│   │
│   └── core/
│       ├── config.py
│       ├── database.py
│       └── security.py
│
├── prompts/
├── migrations/
├── tests/
├── Dockerfile
└── pyproject.toml
```

------------------------------------------------------------------------

# 34. Suggested React Project Structure

``` text
frontend/
├── src/
│   ├── app/
│   ├── components/
│   │   ├── ui/
│   │   ├── project/
│   │   ├── thumbnail/
│   │   ├── editor/
│   │   └── agents/
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── CreateProject.tsx
│   │   ├── Project.tsx
│   │   ├── Concepts.tsx
│   │   └── Editor.tsx
│   │
│   ├── hooks/
│   ├── stores/
│   ├── api/
│   ├── types/
│   └── lib/
│
├── package.json
└── vite.config.ts
```

------------------------------------------------------------------------

# 35. Recommended Tech Stack

## Frontend

  Area           Technology
  -------------- -------------------
  UI             React
  Language       TypeScript
  Build          Vite
  Styling        Tailwind CSS
  Components     shadcn/ui
  State          Zustand
  Server state   TanStack Query
  Forms          React Hook Form
  Validation     Zod
  Animation      Framer Motion
  Editor         Fabric.js / Konva

## Backend

  Area            Technology
  --------------- ------------------------
  Language        Python
  API             FastAPI
  Validation      Pydantic
  ORM             SQLAlchemy
  Database        PostgreSQL
  Queue           Redis
  Workers         Celery / Dramatiq
  Realtime        WebSockets / SSE
  Storage         S3 / Cloudflare R2
  Vector DB       pgvector
  Auth            JWT / OAuth
  Observability   OpenTelemetry + Sentry

## AI

  Area                  Technology
  --------------------- -----------------------------------
  Agent orchestration   Custom Python orchestration layer
  Frontier LLMs         Provider adapters
  Local LLMs            Ollama / vLLM / llama.cpp
  Vision                Vision-capable model providers
  Image generation      Pluggable image provider layer
  Prompt tracing        Langfuse
  Structured output     Pydantic

------------------------------------------------------------------------

# 36. Docker Development Environment

Recommended services:

``` text
docker-compose.yml

services:
  frontend
  backend
  worker
  postgres
  redis
  minio
  langfuse
```

Local model runtime can run separately:

``` text
Ollama
   │
   └── local model
```

For GPU deployments:

``` text
vLLM
   │
   └── local model
```

------------------------------------------------------------------------

# 37. MVP Scope

Do not build everything initially.

## MVP v1

### Input

-   Video description
-   YouTube URL
-   Reference thumbnail upload

### Agents

1.  Orchestrator
2.  Video Analyst
3.  Reference Analyst
4.  Hook Strategist
5.  Creative Director
6.  Visual Director
7.  Image Generator
8.  Critic

### UI

-   Dashboard
-   Create project
-   Reference upload
-   Agent progress
-   4 concept cards
-   Generate selected concept
-   Basic editor
-   Export

### Models

-   One frontier LLM provider
-   Ollama/local model support
-   One image generation provider

This is enough to validate the core product.

------------------------------------------------------------------------

# 38. V2

Add:

-   Multiple image providers
-   Multiple frontier providers
-   Advanced editor
-   Creator profiles
-   Brand kits
-   Thumbnail history
-   Variations
-   Better critique
-   Batch generation
-   More local model support
-   Personal style memory

------------------------------------------------------------------------

# 39. V3

Add:

-   Channel-level learning
-   Historical thumbnail analysis
-   A/B testing workflows
-   Thumbnail performance analytics
-   Automated style extraction
-   Team collaboration
-   Shared brand libraries
-   API access
-   Desktop/local deployment
-   Fully local/private deployment

------------------------------------------------------------------------

# 40. Long-Term Product Architecture

The final product should evolve into:

``` text
                    AI THUMBNAIL SUITE
                           │
           ┌───────────────┼────────────────┐
           │               │                │
       CREATE           ANALYZE          MANAGE
           │               │                │
     ┌─────┼─────┐    ┌────┼────┐      ┌────┼────┐
     │     │     │    │    │    │      │    │    │
   Ideas  Refs  AI   Score Style Trends Projects Brands
           │
           ▼
      AGENT SYSTEM
           │
     ┌─────┼─────────────┐
     │     │             │
   Local Frontier     Vision/Image
    LLMs    LLMs        Models
```

------------------------------------------------------------------------

# 41. Core Design Principles

### 1. Agent-first, not prompt-first

The product should be a workflow of specialized agents.

### 2. Model-agnostic

Agents should not care whether the underlying model is local or
cloud-based.

### 3. Structured state

Use typed project state instead of passing unstructured text between
agents.

### 4. Image generation is only one stage

The differentiator is the reasoning and creative workflow around
generation.

### 5. Human-in-the-loop

Users should be able to select concepts, modify directions, regenerate,
and override AI decisions.

### 6. Iterative generation

Generate → critique → revise should be a core workflow.

### 7. Local-first capability

Users should be able to run supported workflows locally when privacy,
cost, or latency matters.

### 8. Provider abstraction

Adding another LLM or image provider should require implementing an
adapter, not changing the agent system.

### 9. Observable agents

Every agent run should be traceable and debuggable.

### 10. Separate visual generation from composition

Use AI for visual creation and a deterministic editor/compositor for
text and precise layout.

------------------------------------------------------------------------

# 42. Final Architecture

``` text
┌───────────────────────────────────────────────────────────────┐
│                         REACT APP                             │
│                                                               │
│ Dashboard │ Create │ Concepts │ Editor │ Library │ Settings  │
└──────────────────────────────┬────────────────────────────────┘
                               │
                         REST + SSE/WS
                               │
┌──────────────────────────────▼────────────────────────────────┐
│                       FASTAPI BACKEND                         │
│                                                               │
│ Auth │ Projects │ Assets │ Generation │ Export │ Settings     │
└──────────────────────────────┬────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   AGENT ORCHESTRATOR │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼───────────────────────┐
        │                      │                       │
        ▼                      ▼                       ▼
   Video Agent          Reference Agent          Audience Agent
        │                      │                       │
        └──────────────────────┼───────────────────────┘
                               ▼
                       Hook Strategist
                               │
                               ▼
                       Concept Generator
                               │
                               ▼
                       Creative Director
                               │
                               ▼
                         Visual Director
                               │
                               ▼
                         MODEL ROUTER
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
           LOCAL            FRONTIER          VISION
           LLMs              LLMs             MODELS
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                       IMAGE GENERATION
                               │
                               ▼
                         THUMBNAIL CRITIC
                               │
                         ┌─────┴─────┐
                         │           │
                      Revise       Pass
                         │           │
                         └─────►     ▼
                                  EDITOR
                                    │
                                    ▼
                                  EXPORT

        ┌────────────────────────────────────────────────┐
        │ PostgreSQL │ Redis │ S3/R2 │ Observability     │
        └────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 43. Recommended Starting Point

Build the first version around this exact loop:

``` text
Video description
       +
Optional thumbnail references
       +
Optional YouTube URL
       │
       ▼
Video Analyst
       +
Reference Analyst
       │
       ▼
Hook Strategist
       │
       ▼
Creative Director
       │
       ▼
4 Thumbnail Concepts
       │
       ▼
User selects concept
       │
       ▼
Visual Director
       │
       ▼
Image Generator
       │
       ▼
Thumbnail Critic
       │
       ▼
1–2 automatic revisions
       │
       ▼
Final thumbnail
       │
       ▼
React editor
       │
       ▼
Export
```

This keeps the first implementation focused while preserving the
architecture needed for a much larger AI thumbnail platform.
