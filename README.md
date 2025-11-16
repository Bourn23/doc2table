# 🌟⚡ **Lumina**

<p align="center">
  <img src="assets/lumina-banner.png" alt="Lumina - Document Intelligence Platform" width="600"/>
</p>

### **From Unstructured Chaos to Structured Insight | Multi-Agent Document Intelligence**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)]()
[![NVIDIA](https://img.shields.io/badge/NVIDIA-NIM-76B900?logo=nvidia&logoColor=white)]()
[![Google](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white)]()
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?logo=react&logoColor=white)]()

---

## ⚡ Quick Start

Get Lumina running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/Bourn23/doc2table.git
cd doc2table

# 2. Setup environment and credentials (one-time setup)
chmod +x setup-environment.sh
./setup-environment.sh interactive

# 3. Run the deployment script
chmod +x manage-lumina.sh
./manage-lumina.sh

# 4. Select Option 2: Deploy Backend
# 5. Select Option 3: Deploy Frontend
```

**That's it!** Your Lumina instance will be live at the S3 URL shown by the script.

📖 **New to Lumina?** Check out the [Deployment Guide](#-deployment-guide) for detailed instructions.

---

## 📚 Table of Contents

- [Overview](#-overview)
- [The Problem](#the-problem-with-manual-data-extraction)
- [Our Solution](#our-solution-agentic-document-intelligence)
- [Core Stack](#-core-stack)
- [Features](#-features)
- [**🚀 Deployment Guide**](#-deployment-guide) ← **Start Here**
- [Technology Stack Details](#-technology-stack-details)
- [Project Structure](#️-project-structure)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)

---

## 📖 Additional Documentation

- **[Technical Deep Dive](TECHNICAL_DEEP_DIVE.md)** - Comprehensive guide to architecture, AI integration, and implementation details
- **[Hackathon Evaluation](kiro-documentation/hackathon-evaluation/)** - Detailed technical analysis and competitive positioning

---

## 🎯 Overview

**Lumina** is an **intelligent document processing system** that transforms unstructured documents into queryable, structured knowledge. Built on a **multi-agent AI architecture**, it automatically analyzes your documents, designs optimal extraction schemas, extracts data with precision, and enables natural language querying through advanced RAG (Retrieval-Augmented Generation).

> 🔮 *Lumina combines makes document intelligence automated, precise, and conversational. And above all, open-sourced.*

---

## The Problem: Document Analysis Doesn't Scale

**Have you ever needed to analyze dozens of contracts, research papers, or financial reports—only to hit the '10 file upload limit' on every AI tool?**

### Current Reality
- **Manual data extraction costs U.S. companies $28,500 per employee annually**
- Researchers spend **28% of their time** manually extracting data from papers
- Existing AI tools (ChatGPT, Claude) limit you to **10-20 files maximum**
- Academic tools (SciSpace, Elicit) only work with research papers, not business documents
- Enterprise solutions (Hebbia, Palantir) cost **$10,000+ per seat annually**
- **No open-source alternatives** exist that combine scale, validation, and conversational queries

### The Traditional Workflow
1. **Manually design** schemas for each document type
2. **Labor-intensive** reading of all documents
3. **Manually extract** data from PDFs into spreadsheets
4. **Re-read** documents multiple times to answer new questions
5. **Lose context** when documents don't fit your predefined structure

**This is slow, error-prone, and doesn't scale** when you have 20+ documents to analyze.


## Our Solution: Agentic AI for Document Intelligence

We fix this by using **specialized AI agents** that collaborates with the user, understand your documents, design extraction schemas, extract structured data, and answer questions.

### What is Agentic Extraction?

Instead of one large AI model trying to do everything, Lumina uses **seven specialized agents** working together:

- **Document Classifier**: Analyzes document types, domains, and content structure
- **Intention Recommender**: Suggests what data you should extract based on document analysis
- **Schema Designer**: Creates optimized Pydantic models for your extraction task
- **Pydantic Code Generator**: Writes production-ready validation code
- **Extraction Agent**: Extracts structured data from each document in parallel
- **Query Router**: Classifies user questions and routes to the right processing pipeline
- **Answer Synthesizer**: Generates cited answers from retrieved evidence

Unlike single-model systems (which hallucinate), our **agent pipeline is deterministic** — each agent has one job and does it well.

![Lumina Workflow](image-1.png)
---

**Similar Services:**
| Feature | Lumina | ChatGPT/Claude | SciSpace/Elicit | Hebbia/Palantir |
|---------|--------|----------------|-----------------|-----------------|
| File Limit | Unlimited | 10-20 | Research only | Unlimited |
| Validation | ✅ Pydantic | ❌ None | ❌ None | ✅ Custom |
| Open Source | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Cost | ~$32/mo | $20/mo | $20/mo | $10K+/year |
| Custom Schema | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| Citation | ✅ Yes | ⚠️ Limited | ✅ Yes | ✅ Yes |

## 🧩 Core Stack

| Layer | Technology | Purpose |
|-------|-------------|---------|
| **Orchestration** | `OpenAI Agents SDK` | Multi-agent coordination and tool calling |
| **Generation** | `NVIDIA llama-3.1-nemotron-8b` | High-quality text generation for extraction |
| **Embedding** | `NVIDIA llama-3.2-nv-retriever-300m` | Vector embeddings for semantic search |
| **Reranking** | `NVIDIA llama-3.2-nemoretriever-reranker-500m` | Precision reranking of search results |
| **Vector Compute** | `FAISS` | GPU-accelerated similarity search |
| **API Framework** | `FastAPI (Async)` | High-performance async REST API |
| **Database** | `SQLAlchemy (Async) + PostgreSQL/SQLite` | Persistent session and record storage |
| **Knowledge Graph** | `LangChain` | Relationship extraction |
| **Document Processing** | `PyMuPDF (fitz) + pandas` | PDF, CSV, text file parsing |
| **Schema Validation** | `Pydantic V2` | Dynamic model generation with validators |
| **Frontend (UI)** | `React` | Interactive document upload and query interface |

---

## 🚀 Features

### Core Capabilities
- 🤖 **7 Specialized Agents** – Each with a focused task in the extraction pipeline
- 📄 **Multi-Format Processing** – Handles various types of documents including PDFs, CSVs, text files, markdown
- 🧠 **Intelligent Schema Generation** – AI recommends optimal extraction fields
- ⚡ **Parallel Extraction** – Concurrent processing of multiple documents
- 🔍 **Advanced RAG Pipeline** – Embedding → Retrieval → Reranking → Generation
- 🎯 **Dynamic Field Extraction** – Add new fields without reprocessing documents
- 🗺️ **Knowledge Graph Construction** – Automatic relationship discovery
- 💾 **Production-Ready** – Async database, retry logic, error handling

### What Makes Lumina Different
- ✅ **User-in-the-Loop Schema Design** – Review, customize, and edit before extraction
- ✅ **Validation at Every Step** – Code validation, structure checks, retry logic
- ✅ **Citation-Backed Answers** – Every fact traced to source document
- ✅ **Markdown Caching** – Converted documents cached for re-use
- ✅ **Export to CSV/JSON** – Download structured data with timestamps

---

### Lumina's Approach:
```
Query: "What temperature was used for TiO2 synthesis?"

1. Router Agent → Detects 'temperature' field exists → rag_row_wise
2. GPU Search → Retrieves records mentioning TiO2
3. Reranker → Re-sorts by relevance
4. Structured Evidence:
   {
     "material_name": "TiO2 nanoparticles",
     "synthesis.temperature": 350.0,
     "_source_document": "paper_1.pdf"
   }
5. Answer Synthesizer → Uses structured field directly
Answer: "TiO2 was synthesized at 350.0°C (paper_1.pdf:record_0)" ✅
```

**Key Differences:**
- ✅ **Structured Fields**: Extraction validates types (number vs string)
- ✅ **Source Tracking**: Every value traced to document + record ID
- ✅ **No Re-Parsing**: LLM doesn't re-interpret text (uses pre-extracted data)
- ✅ **Validation**: Pydantic ensures data quality (ranges, patterns)

---


---

## 📊 Technology Stack Details

### Multi-Agent Orchestration
- **OpenAI Agents SDK**: Tool calling, structured outputs, agent coordination
- **Retry Logic**: Exponential backoff with timeout for LLM calls

### Embedding & Retrieval
- **NVIDIA NIM Embedder**: `llama-3.2-nemoretriever-300m-embed-v1`
  - 2048-dimensional embeddings
  - Separate encoding for queries vs passages
  - OpenAI-compatible API


### Reranking
- **NVIDIA NIM Reranker**: `llama-3.2-nemoretriever-500m-rerank-v2`
  - Improves precision of top-k results
  - Logit scores for relevance ranking
  - REST API with requests Session

### Generation
- **Gemini 2.5 Flash**: Primary LLM for extraction
   - PyDantic schema generation, extraction
- **NVIDIA llama 3.1 Nemotron 8B**: Primary LLM for query
  - Query router agent
  - Answer synthesis and Knowledge graph generation
  - Structured output with Pydantic models
  - Context window: 1M tokens
- **Ollama (Optional)**: Local model support (coming soon)
  - Qwen 3 0.6B for lightweight extraction
  - Self-hosted alternative to cloud APIs

### Data Storage
- **SQLAlchemy (Async)**:
  - PostgreSQL for production
  - SQLite for development
  - Async sessions with connection pooling
- **Tables**:
  - `sessions`: Extraction jobs with schemas
  - `uploaded_files`: Document metadata
  - `extracted_records`: Structured data (JSONB column)

### Document Processing
- **PyMuPDF (fitz)**: PDF text extraction
  - Page-by-page parsing
  - Handles multi-column layouts
- **pandas**: CSV/Excel processing
- **Markdown Caching**: Converted docs saved to `converted_markdown/`

### Knowledge Graph (Optional)

- **LangChain**: Document → Graph transformation
  - Entity extraction from text
  - Relationship inference

---

## 🏗️ Project Structure

```
lumina/
├── lumina-backend/                 # Backend microservices
│   ├── api_service/               # API Gateway (port 8000)
│   │   ├── main.py               # Orchestrates extraction/query services
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── extraction_service/        # Document processing (port 8001)
│   │   ├── main.py               # Schema generation, data extraction
│   │   ├── Dockerfile
│   │   └── converted_markdown/   # Cached converted documents
│   │
│   ├── query_service/             # RAG and querying (port 8002)
│   │   ├── main.py               # Indexing, semantic search
│   │   ├── Dockerfile
│   │   └── indexes/              # FAISS vector indexes
│   │
│   ├── lumina_agents/             # AI agents package (modular)
│   │   ├── __init__.py           # Package exports
│   │   ├── config.py             # Model configuration & selectors
│   │   ├── tools.py              # Agent tool functions
│   │   ├── schema_agents.py      # Schema generation agents
│   │   ├── extraction_agents.py  # Document extraction pipeline
│   │   ├── analysis_agents.py    # Document classification agents
│   │   ├── query_agents.py       # Query routing & synthesis
│   │   └── rag_agent.py          # RAG system implementation
│   │
│   ├── shared/                    # Shared utilities
│   │   ├── models.py             # SQLAlchemy database models
│   │   ├── database.py           # Async DB setup
│   │   ├── job_manager.py        # Redis-based job tracking
│   │   ├── api_types.py          # Pydantic request/response models
│   │   ├── tools.py              # Shared tool definitions
│   │   ├── utils.py              # Helper functions
│   │   └── aws_client.py         # S3 export utilities
│   │
│   ├── tests/                     # Test files
│   └── docker-compose.yml         # Multi-service orchestration
│
├── lumina-frontend-async/         # React frontend
│   ├── src/
│   │   ├── App.tsx               # Main app, phase orchestration
│   │   ├── components/           # Reusable UI components
│   │   ├── phases/               # Phase-specific views
│   │   ├── store/                # Zustand global state
│   │   ├── types/                # TypeScript definitions
│   │   └── utils/                # API client, job manager
│   │
│   ├── package.json
│   └── Dockerfile                # Nginx production build
│
├── scripts/                       # Deployment scripts
├── manage-lumina.sh              # Main deployment orchestration
├── .env                          # API keys (not committed)
└── README.md
```

### Key Architecture Changes

**Modular Agent Package**: The AI agents have been refactored from monolithic files into a clean, modular package structure (`lumina_agents/`):

- **Before**: Two large files (`agents_collection.py` ~950 lines, `rag_agent.py` ~800 lines) with mixed concerns
- **After**: Seven focused modules with clear separation of concerns

**Benefits**:
- ✅ Easier to locate and modify specific agent functionality
- ✅ Better code organization and maintainability
- ✅ Cleaner imports and exports
- ✅ Production-ready with proper type hints and docstrings
- ✅ No duplicate code or commented-out sections

---



---

## 🚀 Deployment Guide

### Prerequisites

Before deploying Lumina, ensure you have:

1. **AWS Account** with credentials ready
2. **API Keys**:
   - NVIDIA API Key ([Get it here](https://build.nvidia.com/settings/api-keys))
   - Google Gemini API Key ([Get it here](https://aistudio.google.com/api-keys))
3. **Local Tools**:
   - Node.js 24+ (for frontend)
   - Docker (optional, for local testing)
   - SSH key pair for EC2 (or let the script create one)

### Quick Start (5 Minutes)

The easiest way to deploy Lumina is using the setup and management scripts:

```bash
# Step 1: Setup environment (one-time)
chmod +x setup-environment.sh
./setup-environment.sh interactive

# Step 2: Run the deployment manager
chmod +x manage-lumina.sh
./manage-lumina.sh
```

### Step-by-Step Deployment

#### Step 0: Setup Environment (One-Time)

Before deploying, configure your credentials:

```bash
# Run the interactive setup
./setup-environment.sh interactive
```

This will prompt you for:
- **NVIDIA API Key** - Get from [NVIDIA NGC](https://build.nvidia.com/settings/api-keys) (used for both RAG and KG (Knowledge Graph) services)
- **Google Gemini API Key** - Get from [Google AI Studio](https://aistudio.google.com/api-keys) (used for extraction)
- **AWS Credentials** - Access Key ID, Secret Access Key, Region

All credentials are saved to a `.env` file and automatically used by deployment scripts.

#### Step 1: Deploy Backend to AWS EC2

1. **Run the management script**:
   ```bash
   ./manage-lumina.sh
   ```

2. **Select Option 2: Deploy Backend**
   - This will create a t3.medium EC2 instance (~$30/month)
   - Wait for the instance to be created (2-3 minutes)
   - When prompted, choose to deploy the application
   - **API keys from your .env file are automatically configured!**

3. **Verify Backend is Running**:
   ```bash
   # From the management script, select Option 10: Test Endpoints
   # Or manually test:
   curl http://<your-public-ip>:8000/
   ```

#### Step 2: Deploy Frontend to S3

1. **From the management script, select Option 3: Deploy Frontend**

2. **Choose to build the frontend** when prompted
   - The script will automatically configure the correct backend URL
   - Build the frontend (takes 1-2 minutes)
   - Deploy to S3 (recommended)

3. **Access Your Application**:
   - The script will show you the frontend URL
   - Open it in your browser
   - You should see the Lumina interface

#### Step 3: Test the Full System

1. **Upload a test document**:
   - Click "Upload Documents"
   - Select a PDF or CSV file
   - Wait for analysis to complete

2. **Review and confirm the schema**:
   - Review the AI-recommended fields
   - Edit if needed
   - Click "Confirm and Extract"

3. **Query your data**:
   - Try: "Summarize the data"
   - Try: "Create a new column for [something]"
   - Try: "Export as CSV"

### Managing Your Deployment

The `manage-lumina.sh` script provides all the tools you need:

```
1. 🤖 Deploy NIM Models          - Deploy NVIDIA NIM on EKS (optional)
2. 🏗️  Deploy Backend            - Initial backend deployment
3. 🌐 Deploy Frontend            - Initial frontend deployment

4. 📊 Show System Status         - Check if services are running
5. ⏸️  Pause System              - Stop EC2 to save costs
6. ▶️  Resume System             - Restart EC2 instance
7. 🔄 Restart Docker Services    - Restart containers without rebuild
8. 🚀 Redeploy Backend Code      - Deploy code changes to backend
9. 🌐 Redeploy Frontend          - Deploy code changes to frontend

10. 🧪 Test Endpoints            - Verify all services are responding
11. 📋 Show Deployment Info      - Show URLs, IPs, and costs
12. 📜 View Docker Logs          - Debug backend issues
13. 🔧 Fix Frontend Issues       - Fix API URL mismatches

14. 🧹 Clean Up All Resources    - Delete everything (cannot be undone)
```

### Common Deployment Scenarios

#### Scenario 1: Code Changes to Backend

```bash
# 1. Make your code changes locally
# 2. Run the management script
./manage-lumina.sh

# 3. Select Option 8: Redeploy Backend Code
# This will:
# - Copy your updated code to EC2
# - Rebuild Docker containers
# - Restart all services
```

#### Scenario 2: Code Changes to Frontend

```bash
# 1. Make your code changes locally
# 2. Run the management script
./manage-lumina.sh

# 3. Select Option 9: Redeploy Frontend
# This will:
# - Fix .env.production
# - Rebuild the frontend
# - Deploy to S3
```

#### Scenario 3: Debugging Issues

```bash
# View logs
./manage-lumina.sh
# Select Option 12: View Docker Logs

# Check system status
./manage-lumina.sh
# Select Option 4: Show System Status

# Test endpoints
./manage-lumina.sh
# Select Option 10: Test Endpoints
```

#### Scenario 4: Saving Costs

```bash
# Pause the system when not in use
./manage-lumina.sh
# Select Option 5: Pause System

# Resume when needed
./manage-lumina.sh
# Select Option 6: Resume System
```

### Troubleshooting

#### ❌ Frontend shows "Failed to load resource: 404" or "405 Method Not Allowed"

**Problem**: Frontend can't reach the backend API.

**Solution**:
```bash
./manage-lumina.sh
# Select Option 13: Fix Frontend Issues
# Then select Option 5: Fix All Issues
```

This will:
1. Update `.env.production` with correct backend URL
2. Rebuild the frontend
3. Redeploy to S3

#### ❌ Backend services not starting

**Problem**: Docker containers fail to start or crash immediately.

**Solution**: Check the logs:
```bash
./manage-lumina.sh
# Select Option 12: View Docker Logs
```

Common causes:
- **Missing API keys**: Edit `.env` file and add `NVIDIA_API_KEY` and `GOOGLE_GEMINI_API_KEY`
- **Port conflicts**: Another service is using ports 8000, 8001, or 8002
- **Docker build failed**: Check if you have enough disk space

**Fix**:
```bash
# SSH to instance
ssh -i <your-key>.pem ec2-user@<your-ip>

# Edit .env file
nano .env

# Add your API keys, then restart
docker compose -f docker-compose-backend.yml restart
```

#### ❌ "No columns could be queried successfully"

**Problem**: Query service can't find indexes created by extraction service.

**Cause**: Services aren't sharing the `indexed_volume` properly.

**Solution**: Redeploy with the latest code (this was fixed):
```bash
./manage-lumina.sh
# Select Option 8: Redeploy Backend Code
```

#### ❌ "Index 'column_education_history' not found"

**Problem**: Dynamically extracted columns can't be queried.

**Cause**: Column name sanitization mismatch between services.

**Solution**: This was fixed in the latest version. Redeploy:
```bash
./manage-lumina.sh
# Select Option 8: Redeploy Backend Code
```

#### ❌ Frontend shows `[object Object]` in table cells

**Problem**: Nested objects/arrays not displaying correctly.

**Solution**: This was fixed in the latest version. Redeploy frontend:
```bash
./manage-lumina.sh
# Select Option 9: Redeploy Frontend
```

#### ❌ "Request failed with status code 500"

**Problem**: Backend error during processing.

**Solution**: Check backend logs for details:
```bash
./manage-lumina.sh
# Select Option 12: View Docker Logs
# Select Option 2: View specific container logs
# Enter: api-service (or extraction-service, or query-service)
```

Common causes:
- Invalid API keys
- LLM API rate limits exceeded
- Database connection issues

#### ❌ EC2 instance IP changed after restart

**Problem**: After stopping/starting EC2, the public IP changes.

**Solution**: The frontend needs to be updated with the new IP:
```bash
# The new IP is automatically saved to backend-instance-personal.env
# Just redeploy the frontend:
./manage-lumina.sh
# Select Option 9: Redeploy Frontend
```

#### 💡 General Debugging Tips

1. **Check system status first**:
   ```bash
   ./manage-lumina.sh
   # Select Option 4: Show System Status
   ```

2. **Test endpoints**:
   ```bash
   ./manage-lumina.sh
   # Select Option 10: Test Endpoints
   ```

3. **View deployment info**:
   ```bash
   ./manage-lumina.sh
   # Select Option 11: Show Deployment Info
   ```

4. **SSH to instance for manual debugging**:
   ```bash
   ssh -i <your-key>.pem ec2-user@<your-ip>
   
   # Check container status
   docker ps
   
   # View logs
   docker logs api-service
   docker logs extraction-service
   docker logs query-service
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   ```

### Deployment Architecture

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
│                                           │                  │
│                                           ▼                  │
│                                  ┌─────────────────────┐    │
│                                  │  Shared Volumes:    │    │
│                                  │  - uploaded_files   │    │
│                                  │  - indexed_volume   │    │
│                                  │  - exports_data     │    │
│                                  └─────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
            ┌──────────────┐          ┌──────────────┐
            │ NVIDIA NIM   │          │ Google       │
            │ API          │          │ Gemini API   │
            │ (Embedding,  │          │ (Extraction) │
            │  Reranking)  │          │              │
            └──────────────┘          └──────────────┘
```

### Cost Breakdown

**Monthly Costs (when running 24/7):**
- EC2 t3.medium: ~$30/month
- S3 hosting: ~$0.50/month
- Data transfer: ~$1-2/month
- **Total: ~$32/month**

**Cost Saving Tips:**
- Pause the EC2 instance when not in use (Option 5)
- Use spot instances for development
- Delete resources when done (Option 14)

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Restrict EC2 security groups** to your IP only
4. **Rotate API keys** regularly
5. **Enable CloudWatch logs** for monitoring

### Getting API Keys

**NVIDIA API Key:**
1. Go to [NVIDIA NGC](https://catalog.ngc.nvidia.com/)
2. Sign up for a free account
3. Generate an API key from your account settings
4. This key works for embeddings, reranking, and LLM

**Google Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. This key is used for the extraction LLM

### Environment Variables Reference

The `.env` file on your EC2 instance contains all configuration. Here's what each variable does:

```bash
# Database Configuration
POSTGRES_PASSWORD=lumina_postgres_password_2025
DATABASE_URL=postgresql+asyncpg://lumina:lumina_postgres_password_2025@postgres:5432/lumina_db
REDIS_URL=redis://redis:6379

# Service URLs (Docker network names)
EXTRACTION_SERVICE_URL=http://extraction-service:8001
QUERY_SERVICE_URL=http://query-service:8002

# Application Configuration
PYTHONPATH=/app
EXPORTS_BUCKET_NAME=lumina-exports-bucket

# ⚠️ REQUIRED: LLM API Keys
NVIDIA_API_KEY="your-nvidia-api-key-here"           # Get from: https://catalog.ngc.nvidia.com/
GOOGLE_GEMINI_API_KEY="your-google-api-key-here"   # Get from: https://makersuite.google.com/app/apikey

# These reuse the NVIDIA key
NVIDIA_EMBED_API_KEY=$NVIDIA_API_KEY
NVIDIA_RERANK_API_KEY=$NVIDIA_API_KEY
NVIDIA_NIM_API_KEY=$NVIDIA_API_KEY

# LLM Models (can be customized)
GRAPH_LLM_MODEL="nvidia/llama-3.1-nemotron-nano-8b-v1"

# Optional: Neo4j for Knowledge Graphs
NEO4J_URL=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### Advanced Configuration

#### Using Custom Models

Edit `lumina-backend/.env`:
```bash
# Use different NVIDIA models
GRAPH_LLM_MODEL="nvidia/llama-3.1-nemotron-70b-instruct"

# Use OpenAI instead
LLM_PROVIDER=openai
OPENAI_API_KEY="your-openai-key"
```

#### Scaling for Production

For production workloads:
1. **Compute**: Use larger EC2 instances (t3.large or t3.xlarge)
2. **Database**: Enable RDS PostgreSQL instead of containerized Postgres
3. **CDN**: Use CloudFront CDN for the S3 frontend
4. **Auto-scaling**: Set up EC2 auto-scaling groups
5. **Monitoring**: Enable CloudWatch alarms for CPU, memory, and errors
6. **Load Balancing**: Add an Application Load Balancer for high availability
7. **Backup**: Enable automated RDS backups and S3 versioning

---

## 🗺️ Roadmap

### Phase 1: Core Intelligence (Current)
- ✅ Multi-agent extraction pipeline
- ✅ GPU-accelerated RAG
- ✅ Dynamic field extraction
- ✅ Knowledge graph construction

### Phase 2: Enhanced Capabilities 
- [ ] **Table Extraction**: Dedicated agent for query generation and extracting data from complex tables
- [ ] **Image Analysis**: Extract data from charts/figures (OCR + VLM)
- [ ] **Custom Validators**: User-defined validation logic


---

## 🤝 Contributing

We welcome contributions! Here's how:



## 🌟 Recognition

Built by researchers, for researchers who are tired of manual data extraction.

**Core Innovation:**
- Multi-agent architecture where each agent has a single, focused task
- Dynamic schema generation and on-demand field extraction
- GPU-accelerated retrieval with structured evidence for hallucination reduction
- Markdown caching for fast re-extraction without re-upload

**Key Technologies:**
- OpenAI Agents SDK for agentic coordination
- NVIDIA NIM for embedding and reranking and high-quality generation

---

### Architecture Overview

```mermaid
graph TB
    subgraph "Document Analysis Phase"
        A[Upload Documents] -->|Async Processing| B[Document Classifier Agent]
        B -->|Classifications| C[Intention Recommender Agent]
        C -->|Recommended Schema| D{User Review & Edit}
    end
    
    subgraph "Schema Generation Phase"
        D -->|User Intention + Fields| E[Schema Designer Agent]
        E -->|Field Recommendations| F[Pydantic Code Agent]
        F -->|Validate Code| G[Code Validator Tool]
        G -->|Check Structure| H[Structure Validator Tool]
        F -->|Generate Model| I[Extraction Prompt Agent]
        F -->|Generate Model| J[Field Mapping Agent]
    end
    
    subgraph "Parallel Extraction Phase"
        I & J -->|Dynamic Model| K[Data Extraction Pipeline]
        K -->|Fan-Out| L1[Extract Doc 1]
        K -->|Fan-Out| L2[Extract Doc 2]
        K -->|Fan-Out| L3[Extract Doc N]
        
        L1 & L2 & L3 -->|Structured Records| M[Database Storage]
        L1 & L2 & L3 -->|Text Chunks| N[Markdown Cache]
    end
    
    subgraph "RAG Indexing Phase"
        M -->|Records| O[Chunking Strategy]
        O -->|Row-wise Chunks| P[NVIDIA Embedding API]
        O -->|Column Chunks| Q[NVIDIA Embedding API]
        P & Q -->|Vectors| R[GPU Vector Store]
    end
    
    subgraph "Query Processing Phase"
        S[User Query] -->|Natural Language| T[Query Router Agent]
        
        T -->|rag_row_wise| U1[Row Retrieval]
        T -->|rag_column_wise| U2[Column Retrieval]
        T -->|dynamic_extraction| U3[Dynamic Extractor]
        T -->|function| U4[Function Handler]
        
        U1 & U2 -->|Embed Query| V[NVIDIA Embedding]
        V -->|GPU Cosine Similarity| W[Top-K Retrieval]
        W -->|Rerank| X[NVIDIA Reranker]
        X -->|Context| Y[Answer Synthesizer]
        
        U3 -->|New Field| Z1[Schema Designer]
        Z1 -->|Extract| Z2[Parallel Extraction]
        Z2 -->|Updated Records| M
        
        U4 -->|Export CSV| AA[File Export Tool]
        
        Y -->|LLM Call| AB[Gemini Generator]
        AB -->|Cited Answer| AC[Response + Sources]
    end
    
    subgraph "Optional: Knowledge Graph"
        X -->|Retrieved Chunks| KG1[LangChain Graph Transformer]
        KG1 -->|Nodes & Edges| KG2[Neo4j Database]
        KG2 -->|Graph Query| KG3[Relationship Discovery]
    end
```

<div align="center">

**From Chaos to Clarity**: Where multi-agent AI meets document intelligence to extract the knowledge hidden in your papers.

---

## 📖 Learn More

### For Users
- **[Quick Start Guide](#-quick-start)** - Get running in 5 minutes
- **[Deployment Guide](#-deployment-guide)** - Detailed deployment instructions
- **[Troubleshooting](#troubleshooting)** - Common issues and solutions

### For Developers
- **[Technical Deep Dive](TECHNICAL_DEEP_DIVE.md)** - Architecture, AI integration, and implementation
- **[Project Structure](#️-project-structure)** - Codebase organization
- **[Contributing](#-contributing)** - How to contribute

### For Evaluators
- **[Hackathon Evaluation](kiro-documentation/hackathon-evaluation/)** - Technical analysis and scoring
- **[Competitive Analysis](kiro-documentation/hackathon-evaluation/COMPETITIVE_ANALYSIS.md)** - Market positioning

[⬆ back to top](#-lumina)

</div>
