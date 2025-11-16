# Lumina - Technical Deep Dive

**A Comprehensive Guide to Lumina's Architecture, AI Integration, and Implementation**

> 📚 **For Users & Developers:** This document provides detailed technical insights into how Lumina works under the hood. Perfect for those who want to understand the system architecture, AI integration, or contribute to the project.

---

## 📖 Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Multi-Agent AI System](#multi-agent-ai-system)
3. [NVIDIA NIM Integration](#nvidia-nim-integration)
4. [RAG Pipeline Deep Dive](#rag-pipeline-deep-dive)
5. [Data Flow & Processing](#data-flow--processing)
6. [Database Schema & Storage](#database-schema--storage)
7. [Frontend Architecture](#frontend-architecture)
8. [Deployment & Infrastructure](#deployment--infrastructure)
9. [Performance & Optimization](#performance--optimization)
10. [Security & Best Practices](#security--best-practices)

---

## System Architecture Overview

### High-Level Architecture

Lumina uses a **microservices architecture** with three main services that communicate via HTTP and share data through Docker volumes:

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (React + TypeScript)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Port 8000)                     │
│  - Request orchestration                                         │
│  - File upload handling                                          │
│  - Job status management (Redis pub/sub)                         │
└─────────────────────────────────────────────────────────────────┘
         ↓                                              ↓
┌──────────────────────────┐          ┌──────────────────────────┐
│  Extraction Service      │          │  Query Service           │
│  (Port 8001)             │          │  (Port 8002)             │
│                          │          │                          │
│  - Document analysis     │          │  - RAG indexing          │
│  - Schema generation     │          │  - Semantic search       │
│  - Data extraction       │          │  - Answer generation     │
│  - 7 AI Agents           │          │  - Knowledge graphs      │
└──────────────────────────┘          └──────────────────────────┘
         ↓                                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure                         │
│  - PostgreSQL (structured data)                                  │
│  - Redis (job queue & pub/sub)                                   │
│  - FAISS (vector indexes)                                        │
│  - Docker Volumes (files, indexes, exports)                      │
└─────────────────────────────────────────────────────────────────┘
```

### Why Microservices?


1. **Separation of Concerns:** Each service has a focused responsibility
2. **Independent Scaling:** Scale extraction and query services independently
3. **Fault Isolation:** If one service fails, others continue working
4. **Technology Flexibility:** Each service can use different tech stacks
5. **Development Velocity:** Teams can work on services independently

### Service Communication

**Synchronous (HTTP):**
- API Gateway → Extraction Service: `/analyze`, `/extract`
- API Gateway → Query Service: `/index`, `/query`

**Asynchronous (Redis Pub/Sub):**
- Job status updates broadcast to all subscribers
- Real-time progress tracking for long-running tasks

---

## Multi-Agent AI System

### The 7 Specialized Agents

Lumina uses **7 specialized AI agents** instead of a single monolithic LLM. Each agent has a focused task:

#### 1. **Document Classifier Agent**
**Purpose:** Analyzes document types, domains, and content structure

**Input:** First few paragraphs of each document  
**Output:** `DocumentClassification` (Pydantic model)
```python
{
  "document_types": ["research_paper", "technical_report"],
  "domains": ["materials_science", "nanotechnology"],
  "content_structure": "structured_with_tables",
  "recommended_approach": "table_extraction"
}
```

**Model Used:** Gemini 2.5 Flash (fast classification)

---

#### 2. **Intention Recommender Agent**
**Purpose:** Suggests what data should be extracted based on document analysis

**Input:** Document classifications + user context  
**Output:** `IntentionRecommendation` (Pydantic model)
```python
{
  "recommended_intention": "Extract material properties and synthesis conditions",
  "field_recommendations": [
    {
      "field_name": "material_name",
      "field_type": "string",
      "rationale": "Core entity in materials science papers"
    },
    {
      "field_name": "synthesis_temperature",
      "field_type": "float",
      "rationale": "Critical parameter for reproducibility"
    }
  ]
}
```

**Model Used:** Gemini 2.5 Flash

---

#### 3. **Schema Designer Agent**
**Purpose:** Creates optimized Pydantic models for extraction

**Input:** User intention + field recommendations  
**Output:** `SchemaRecommendation` (Pydantic model)
```python
{
  "fields": [
    {
      "name": "material_name",
      "type": "str",
      "description": "Name of the material being studied",
      "required": True
    },
    {
      "name": "synthesis_temperature",
      "type": "float",
      "description": "Temperature in Celsius",
      "required": False,
      "constraints": "Must be between -273.15 and 5000"
    }
  ]
}
```

**Model Used:** Gemini 2.5 Flash

---

#### 4. **Pydantic Code Generator Agent**
**Purpose:** Writes production-ready Pydantic model code

**Input:** Schema recommendation  
**Output:** `PydanticModelCode` (executable Python code)
```python
from pydantic import BaseModel, Field

class ExtractionModel(BaseModel):
    material_name: str = Field(description="Name of the material")
    synthesis_temperature: Optional[float] = Field(
        None, 
        ge=-273.15, 
        le=5000,
        description="Temperature in Celsius"
    )
```

**Validation:** Code is validated for syntax and structure before use

**Model Used:** Gemini 2.5 Flash

---

#### 5. **Extraction Agent**
**Purpose:** Extracts structured data from documents

**Input:** Document text + Pydantic model + extraction prompt  
**Output:** List of extracted records (validated against Pydantic model)

**Process:**
1. Convert document to markdown (cached for re-use)
2. Extract first paragraphs for context
3. Call LLM with structured output (Pydantic model)
4. Validate extracted data
5. Retry on validation errors (up to 3 times)

**Model Used:** Gemini 2.5 Flash (high-quality extraction)

---

#### 6. **Query Router Agent**
**Purpose:** Classifies user queries and routes to appropriate handler

**Input:** User query + available columns  
**Output:** `QueryIntent` (Pydantic model)
```python
{
  "intent_type": "rag_row_wise",  # or "rag_column_wise", "dynamic_extraction", "function"
  "target_columns": ["material_name", "synthesis_temperature"],
  "reasoning": "User asking about specific material property"
}
```

**Routing Logic:**
- `rag_row_wise`: Retrieve full records (e.g., "What materials were studied?")
- `rag_column_wise`: Retrieve specific column (e.g., "List all temperatures")
- `dynamic_extraction`: Extract new field (e.g., "Add equipment_used column")
- `function`: Execute function (e.g., "Export to CSV")

**Model Used:** NVIDIA llama-3.1-nemotron-nano-8b-v1 ⭐ (required model)

---

#### 7. **Answer Synthesizer Agent**
**Purpose:** Generates natural language answers from retrieved evidence

**Input:** User query + retrieved records (with citations)  
**Output:** Natural language answer with source citations

**Example:**
```
Query: "What temperature was used for TiO2 synthesis?"

Retrieved Evidence:
{
  "material_name": "TiO2 nanoparticles",
  "synthesis_temperature": 350.0,
  "_source_document": "paper_1.pdf",
  "_record_id": 0
}

Answer: "TiO2 nanoparticles were synthesized at 350.0°C 
         (Source: paper_1.pdf, Record #0)"
```

**Model Used:** NVIDIA llama-3.1-nemotron-nano-8b-v1 ⭐ (required model)

---

### Agent Orchestration

**Framework:** OpenAI Agents SDK  
**Features:**
- Tool calling for validation and processing
- Structured outputs (Pydantic models)
- Retry logic with exponential backoff
- Async execution for parallel processing

**Example Agent Definition:**
```python
from agents import Agent
from lumina_agents import gemini_model, CustomAgentHooks

schema_agent = Agent(
    name="schema_designer",
    model=gemini_model,
    instructions="Design optimal extraction schemas...",
    output_type=SchemaRecommendation,
    tools=[verify_pydantic_model_code, validate_structure],
    hooks=CustomAgentHooks(display_name="Schema Designer", verbose=True)
)
```

---

## NVIDIA NIM Integration

### Three NVIDIA NIMs Used

Lumina integrates **3 NVIDIA NIM models** for different tasks:

#### 1. **Generation NIM** (Required)
**Model:** `nvidia/llama-3.1-nemotron-nano-8b-v1`  
**Purpose:** Query routing and answer synthesis  
**API:** OpenAI-compatible  
**Context Window:** 1M tokens

**Usage:**
```python
from openai import AsyncOpenAI

nim_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

response = await nim_client.chat.completions.create(
    model="nvidia/llama-3.1-nemotron-nano-8b-v1",
    messages=[{"role": "user", "content": query}]
)
```

---

#### 2. **Embedding NIM** (Required)
**Model:** `nvidia/llama-3.2-nemoretriever-300m-embed-v1`  
**Purpose:** Text embedding for semantic search  
**Dimension:** 1024  
**API:** OpenAI-compatible embeddings endpoint

**Usage:**
```python
response = embed_client.embeddings.create(
    input=["text to embed"],
    model="nvidia/llama-3.2-nemoretriever-300m-embed-v1",
    encoding_format="float",
    extra_body={"input_type": "passage", "truncate": "NONE"}
)
embedding = response.data[0].embedding  # 1024-dim vector
```

**Input Types:**
- `"query"`: For user queries (optimized for search)
- `"passage"`: For documents (optimized for retrieval)

---

#### 3. **Reranking NIM** (Bonus)
**Model:** `nvidia/llama-3.2-nemoretriever-500m-rerank-v2`  
**Purpose:** Rerank retrieved documents for better precision  
**API:** REST API with logit scores

**Usage:**
```python
payload = {
    "model": "nvidia/llama-3.2-nemoretriever-500m-rerank-v2",
    "query": {"text": user_query},
    "passages": [{"text": doc1}, {"text": doc2}, ...]
}

response = requests.post(
    "https://ai.api.nvidia.com/v1/retrieval/.../reranking",
    headers={"Authorization": f"Bearer {api_key}"},
    json=payload
)

rankings = response.json()["rankings"]
# [{"index": 0, "logit": 0.95}, {"index": 1, "logit": 0.82}, ...]
```

---

### Why These Models?

**llama-3.1-nemotron-nano-8b-v1:**
- ✅ Required by hackathon
- ✅ Excellent reasoning capabilities
- ✅ 1M token context window
- ✅ Fast inference (8B parameters)

**llama-3.2-nemoretriever-300m-embed-v1:**
- ✅ Optimized for retrieval tasks
- ✅ Separate query/passage encoding
- ✅ 1024-dim embeddings (good balance)
- ✅ Fast embedding generation

**llama-3.2-nemoretriever-500m-rerank-v2:**
- ✅ Improves retrieval precision
- ✅ Logit scores for ranking
- ✅ Handles up to 100 passages
- ✅ Reduces false positives

---

## RAG Pipeline Deep Dive

### Complete RAG Workflow

```
User Query
    ↓
1. EMBEDDING (NVIDIA NIM)
   - Convert query to 1024-dim vector
   - Use "query" input type
    ↓
2. RETRIEVAL (FAISS)
   - GPU-accelerated cosine similarity
   - Retrieve top-20 most similar chunks
   - L2 normalization for accuracy
    ↓
3. RERANKING (NVIDIA NIM)
   - Rerank top-20 to top-5
   - Use logit scores for precision
   - Filter out irrelevant results
    ↓
4. GENERATION (NVIDIA NIM)
   - Synthesize answer from top-5
   - Include source citations
   - Structured output format
    ↓
Answer + Citations
```

### 1. Document Chunking Strategy

**Row-Wise Chunking:**
```python
# Each table row becomes a chunk
chunk = {
    "text": "| Material | Temperature | Pressure |",
    "metadata": {
        "row_id": 0,
        "source_file": "paper_1.pdf",
        "extracted_fields": {...}
    }
}
```

**Column-Wise Chunking:**
```python
# Each column becomes a chunk
chunk = {
    "text": "synthesis_temperature: 350.0, 400.0, 450.0, ...",
    "metadata": {
        "column_name": "synthesis_temperature",
        "source_file": "paper_1.pdf"
    }
}
```

---

### 2. Embedding Generation

**Batch Processing:**
```python
# Process 32 chunks at a time
batch_size = 32
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    embeddings = embed_client.embeddings.create(
        input=batch,
        model="nvidia/llama-3.2-nemoretriever-300m-embed-v1",
        extra_body={"input_type": "passage"}
    )
```

**Optimization:**
- Batch processing reduces API calls
- Async operations for parallel processing
- Caching to avoid re-embedding

---

### 3. FAISS Indexing

**Index Type:** `IndexFlatIP` (Inner Product)  
**Why:** Fast, exact search with L2-normalized vectors (equivalent to cosine similarity)

**Index Creation:**
```python
import faiss
import numpy as np

# Normalize embeddings
embeddings = np.array(embeddings, dtype='float32')
faiss.normalize_L2(embeddings)

# Create index
d = embeddings.shape[1]  # 1024 dimensions
index = faiss.IndexFlatIP(d)
index.add(embeddings)
```

**Search:**
```python
# Normalize query
query_embedding = np.array(query_embedding, dtype='float32').reshape(1, -1)
faiss.normalize_L2(query_embedding)

# Search
distances, indices = index.search(query_embedding, k=20)
```

**Performance:**
- GPU-accelerated (if available)
- Sub-millisecond search for 10K documents
- Scales to millions of documents

---

### 4. Reranking

**Why Rerank?**
- Embedding models optimize for recall (find all relevant docs)
- Reranker optimizes for precision (rank most relevant first)
- Reduces false positives in top results

**Process:**
```python
# Initial retrieval: top-20
retrieved = retrieve(query, top_k=20)

# Rerank to top-5
reranked = rerank(query, retrieved, top_k=5)

# Use top-5 for generation
answer = generate(query, reranked[:5])
```

---

### 5. Answer Generation

**Prompt Template:**
```python
prompt = f"""
You are a helpful assistant. Answer the query based ONLY on the provided context.
If the answer cannot be found, state that clearly.

QUERY: {query}

CONTEXT:
{context_from_top_5_chunks}

ANSWER:
"""
```

**Structured Output:**
```python
{
    "answer": "TiO2 was synthesized at 350.0°C",
    "citations": [
        {
            "source_document": "paper_1.pdf",
            "record_id": 0,
            "confidence": 0.95
        }
    ]
}
```

---

## Data Flow & Processing

### Complete Extraction Flow

```
1. USER UPLOADS FILES
   ↓
2. API GATEWAY
   - Save files to /data/uploaded_files
   - Create session in PostgreSQL
   - Trigger analysis job
   ↓
3. EXTRACTION SERVICE: ANALYSIS
   - Document Classifier Agent analyzes each file
   - Intention Recommender Agent suggests schema
   - Return recommendations to user
   ↓
4. USER REVIEWS SCHEMA
   - Edit field names, types, descriptions
   - Add/remove fields
   - Confirm extraction
   ↓
5. EXTRACTION SERVICE: SCHEMA GENERATION
   - Schema Designer Agent creates Pydantic model
   - Pydantic Code Generator writes code
   - Validate code syntax and structure
   ↓
6. EXTRACTION SERVICE: DATA EXTRACTION
   - Convert documents to markdown (parallel)
   - Extract data using Extraction Agent (parallel)
   - Validate against Pydantic model
   - Save to PostgreSQL
   ↓
7. QUERY SERVICE: INDEXING
   - Chunk extracted records (row-wise + column-wise)
   - Generate embeddings (NVIDIA NIM)
   - Create FAISS index
   - Save index to /data/indexes
   ↓
8. READY FOR QUERIES
```

### Parallel Processing

**Document Extraction:**
```python
# Process 4 documents concurrently
semaphore = asyncio.Semaphore(4)

async def extract_with_limit(file_path):
    async with semaphore:
        return await extract_from_single_document(file_path)

tasks = [extract_with_limit(f) for f in files]
results = await asyncio.gather(*tasks)
```

**Benefits:**
- 4x faster extraction for 10 documents
- Controlled concurrency (avoid rate limits)
- Graceful error handling (one failure doesn't stop others)

---

## Database Schema & Storage

### PostgreSQL Tables

#### 1. **sessions**
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_intention TEXT,
    pydantic_schema_code TEXT,  -- Generated Pydantic model
    extraction_prompt TEXT,
    field_mapping JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 2. **uploaded_files**
```sql
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    filename TEXT,
    file_path TEXT,
    file_size INTEGER,
    mime_type TEXT,
    uploaded_at TIMESTAMP
);
```

#### 3. **extracted_records**
```sql
CREATE TABLE extracted_records (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    source_file_id UUID REFERENCES uploaded_files(id),
    extracted_data JSONB,  -- Flexible schema
    created_at TIMESTAMP
);
```

**Why JSONB?**
- Dynamic schema (different sessions have different fields)
- Indexable (can query specific fields)
- Efficient storage (binary format)

---

### Docker Volumes

**Shared Volumes:**
```yaml
volumes:
  postgres_data:           # Database persistence
  uploaded_files_volume:   # Original uploaded files
  exports_data:            # CSV/JSON exports
  indexed_volume:          # FAISS vector indexes
```

**Why Volumes?**
- Data persists across container restarts
- Shared between services (extraction + query)
- Easy backup and migration

---

## Frontend Architecture

### React + TypeScript Stack

**Core Technologies:**
- React 18.2 (UI framework)
- TypeScript 5.3 (type safety)
- Vite 5.0 (build tool, fast HMR)
- Zustand 4.4 (state management)
- TailwindCSS 3.3 (styling)

### State Management (Zustand)

**Why Zustand?**
- Lightweight (1KB gzipped)
- No boilerplate (vs. Redux)
- TypeScript-first
- React hooks integration

**Store Structure:**
```typescript
interface AppState {
  // Phase management
  phase: Phase;
  setPhase: (phase: Phase) => void;
  
  // Session data
  sessionId: string | null;
  uploadedFiles: UploadedFile[];
  
  // Schema
  recommendedSchema: SchemaRecommendation | null;
  confirmedSchema: ExtractionSchema | null;
  
  // Extracted data
  extractedRecords: ExtractedRecord[];
  
  // Query
  currentQuery: string;
  queryResults: QueryResult | null;
}
```

### Phase-Based Workflow

**8 Phases:**
```typescript
enum Phase {
  IDLE = "IDLE",                    // Initial state
  UPLOADING = "UPLOADING",          // Files being uploaded
  ANALYZING = "ANALYZING",          // AI analyzing documents
  SCHEMA_REVIEW = "SCHEMA_REVIEW",  // User reviews schema
  PROCESSING = "PROCESSING",        // Extracting data
  READY = "READY",                  // Ready for queries
  QUERYING = "QUERYING",            // Processing query
  INSIGHT = "INSIGHT"               // Displaying results
}
```

**State Transitions:**
```
IDLE → UPLOADING → ANALYZING → SCHEMA_REVIEW → 
PROCESSING → READY → QUERYING → INSIGHT → READY
```

### Real-Time Updates (WebSocket)

**Job Status Tracking:**
```typescript
const jobManager = new JobManager(sessionId);

jobManager.on('progress', (data) => {
  console.log(`Progress: ${data.progress}%`);
  updateProgressBar(data.progress);
});

jobManager.on('complete', (data) => {
  console.log('Job complete!');
  setPhase(Phase.READY);
});

jobManager.on('error', (error) => {
  console.error('Job failed:', error);
  showErrorBanner(error.message);
});
```

---

## Deployment & Infrastructure

### AWS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
│                                                              │
│  ┌────────────────────┐         ┌─────────────────────┐    │
│  │   S3 Bucket        │         │   EC2 Instance      │    │
│  │   (Frontend)       │         │   (t3.medium)       │    │
│  │                    │         │                     │    │
│  │  React App         │────────▶│  Docker Compose:    │    │
│  │  (Static Files)    │  API    │  - API Service      │    │
│  │                    │  Calls  │  - Extraction Svc   │    │
│  └────────────────────┘         │  - Query Service    │    │
│                                  │  - PostgreSQL       │    │
│                                  │  - Redis            │    │
│                                  └─────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Automated Deployment

**One-Command Setup:**
```bash
./manage-lumina.sh
```

**Features:**
- EC2 instance creation and configuration
- Docker Compose deployment
- S3 bucket creation and static hosting
- Environment variable management
- Health checks and monitoring

### Cost Optimization

**Monthly Costs:**
- EC2 t3.medium: ~$30/month (730 hours)
- S3 hosting: ~$0.50/month (1GB storage + transfer)
- Data transfer: ~$1-2/month
- **Total: ~$32/month**

**Cost Saving Tips:**
- Stop EC2 when not in use (pay only for hours used)
- Use spot instances for development
- Enable S3 lifecycle policies for old exports

---

## Performance & Optimization

### Extraction Performance

**Benchmarks (10 documents):**
- Sequential: ~5 minutes
- Parallel (4 concurrent): ~1.5 minutes
- **Speedup: 3.3x**

**Optimization Techniques:**
1. Markdown caching (avoid re-parsing PDFs)
2. Parallel extraction (4 concurrent documents)
3. Batch embedding (32 chunks at a time)
4. Connection pooling (database)

### Query Performance

**Benchmarks (10K records):**
- Embedding generation: ~100ms
- FAISS search: <10ms
- Reranking (20 docs): ~200ms
- Answer generation: ~1-2s
- **Total: ~1.5-2.5s**

**Optimization Techniques:**
1. GPU-accelerated FAISS (if available)
2. Index caching (avoid re-indexing)
3. Async operations (parallel API calls)
4. L2 normalization (faster cosine similarity)

---

## Security & Best Practices

### API Key Management

**Environment Variables:**
```bash
# Never commit to git
NVIDIA_API_KEY=nvapi-xxx
GOOGLE_GEMINI_API_KEY=AIzaSy-xxx
```

**Best Practices:**
- Use `.env` files (not committed)
- Rotate keys regularly
- Use separate keys for dev/prod
- Monitor API usage

### Data Security

**File Upload:**
- Validate file types (PDF, CSV, text only)
- Limit file size (100MB max)
- Scan for malware (optional)
- Store in isolated directory

**Database:**
- Use strong passwords
- Enable SSL/TLS connections
- Regular backups
- Access control (least privilege)

### Docker Security

**Best Practices:**
- Non-root users in containers
- Read-only file systems where possible
- Network isolation (internal networks)
- Regular image updates

---

## Contributing & Extending

### Adding a New Agent

1. Create agent file in `lumina_agents/`
2. Define Pydantic output model
3. Write agent instructions
4. Add tools (if needed)
5. Export from `__init__.py`

**Example:**
```python
# lumina_agents/my_agent.py
from agents import Agent
from pydantic import BaseModel

class MyOutput(BaseModel):
    result: str

my_agent = Agent(
    name="my_agent",
    model=gemini_model,
    instructions="Do something useful...",
    output_type=MyOutput
)
```

### Adding a New NIM Model

1. Update `config.py` with model name
2. Create client instance
3. Update agent to use new model
4. Test thoroughly

---

## Additional Resources

### Documentation
- [Main README](README.md) - Quick start and overview
- [Hackathon Evaluation](kiro-documentation/hackathon-evaluation/) - Detailed analysis
- [Deployment Guide](README.md#-deployment-guide) - Step-by-step deployment

### Code Structure
- [Agent Package](lumina-backend/lumina_agents/) - AI agents implementation
- [RAG System](lumina-backend/lumina_agents/rag_agent.py) - RAG pipeline
- [API Service](lumina-backend/api_service/) - API gateway
- [Frontend](lumina-frontend-async/) - React application

### External Links
- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/)
- [OpenAI Agents SDK](https://github.com/openai/agents-sdk)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated:** November 16, 2025  
**Maintained By:** Lumina Team  
**License:** Open Source

For questions or contributions, see the main [README](README.md).
