# 🚀 Detailed Deployment Instructions

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

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                           │
│                                                             │
│  ┌────────────────────┐         ┌─────────────────────┐     │
│  │   S3 Bucket        │         │   EC2 Instance      │     │
│  │   (Frontend)       │         │   (t3.medium)       │     │
│  │                    │         │                     │     │
│  │  React App         │────────▶│  Docker Compose:    │     │
│  │  (Static Files)    │  API    │  - API Service      │     │
│  │                    │  Calls  │  - Extraction Svc   │     │
│  └────────────────────┘         │  - Query Service    │     │
│                                 │  - PostgreSQL       │     │
│                                 │  - Redis            │     │
│                                 └─────────────────────┘     │
│                                           │                 │
│                                           ▼                 │
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


[⬆ back to main page](README.md)