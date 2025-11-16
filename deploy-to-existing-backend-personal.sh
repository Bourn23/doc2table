#!/bin/bash

# Deploy application to existing personal AWS backend instance
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying to Personal AWS Backend Instance${NC}"

# Load backend instance info
if [ ! -f "backend-instance-personal.env" ]; then
    echo -e "${RED}❌ backend-instance-personal.env not found${NC}"
    echo -e "${YELLOW}💡 Run ./deploy-backend-personal-aws.sh first${NC}"
    exit 1
fi

source backend-instance-personal.env

echo -e "${YELLOW}📋 Target Instance: $PUBLIC_IP${NC}"

# Check if instance is running
INSTANCE_STATE=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name' --output text)

if [ "$INSTANCE_STATE" != "running" ]; then
    echo -e "${RED}❌ Instance $INSTANCE_ID is not running (state: $INSTANCE_STATE)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Instance is running${NC}"

# Create docker-compose file for personal AWS (no NIM dependency)
create_docker_compose_personal() {
    cat > docker-compose-backend-personal.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres
    environment:
      POSTGRES_USER: lumina
      POSTGRES_PASSWORD: lumina_secure_password_2024
      POSTGRES_DB: lumina_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lumina -d lumina_db"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - lumina-network

  redis:
    image: "redis:alpine"
    container_name: redis
    ports:
      - "6379:6379"
    networks:
      - lumina-network

  extraction-service:
    build: 
      context: ./lumina-backend
      dockerfile: ./extraction_service/Dockerfile
    container_name: extraction-service
    working_dir: /app/extraction_service
    command: uvicorn main:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    volumes:
      - ./lumina-backend:/app
      - uploaded_files_volume:/data/uploaded_files
      - indexed_volume:/data/indexes
      - exports_data:/data/exports
    environment:
      - PYTHONPATH=/app
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://lumina:lumina_secure_password_2024@postgres:5432/lumina_db
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - lumina-network
    env_file:
      - ./.env

  query-service:
    build: 
      context: ./lumina-backend
      dockerfile: ./query_service/Dockerfile
    container_name: query-service
    working_dir: /app/query_service
    command: uvicorn main:app --host 0.0.0.0 --port 8002
    ports:
      - "8002:8002"
    volumes:
      - ./lumina-backend:/app
      - uploaded_files_volume:/data/uploaded_files
      - indexed_volume:/data/indexes
      - exports_data:/data/exports
    environment:
      - PYTHONPATH=/app
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://lumina:lumina_secure_password_2024@postgres:5432/lumina_db
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - lumina-network
    env_file:
      - ./.env

  api-service:
    build: 
      context: ./lumina-backend
      dockerfile: ./api_service/Dockerfile
    container_name: api-service
    ports:
      - "8000:8000"
    working_dir: /app/api_service
    volumes:
      - ./lumina-backend:/app
      - uploaded_files_volume:/data/uploaded_files
      - exports_data:/data/exports
    environment:
      - PYTHONPATH=/app
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://lumina:lumina_secure_password_2024@postgres:5432/lumina_db
      - EXTRACTION_SERVICE_URL=http://extraction-service:8001
      - QUERY_SERVICE_URL=http://query-service:8002
    depends_on:
      extraction-service:
        condition: service_started
      query-service:
        condition: service_started
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - lumina-network
    env_file:
      - ./.env

networks:
  lumina-network:
    driver: bridge

volumes:
  postgres_data:
  uploaded_files_volume:
  indexed_volume:
  exports_data:
EOF
}

# Create environment file for personal AWS
create_env_file_personal() {
    # Load API keys from root .env file if it exists
    if [ -f ".env" ]; then
        echo -e "${BLUE}📋 Loading API keys from .env file...${NC}"
        source .env
        
        # Check if required keys are set
        if [ -z "$NVIDIA_API_KEY" ] || [ "$NVIDIA_API_KEY" = "nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ]; then
            echo -e "${RED}❌ NVIDIA_API_KEY not set in .env file${NC}"
            echo -e "${YELLOW}💡 Please run: ./setup-environment.sh${NC}"
            exit 1
        fi
        
        if [ -z "$GOOGLE_GEMINI_API_KEY" ] || [ "$GOOGLE_GEMINI_API_KEY" = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" ]; then
            echo -e "${RED}❌ GOOGLE_GEMINI_API_KEY not set in .env file${NC}"
            echo -e "${YELLOW}💡 Please run: ./setup-environment.sh${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ API keys loaded from .env${NC}"
    else
        echo -e "${RED}❌ .env file not found${NC}"
        echo -e "${YELLOW}💡 Please run: ./setup-environment.sh first${NC}"
        exit 1
    fi
    
    # Create .env.personal with values from root .env
    cat > .env.personal << EOF
# Database Configuration
POSTGRES_PASSWORD=lumina_postgres_password_2025
DATABASE_URL=postgresql+asyncpg://lumina:lumina_postgres_password_2025@postgres:5432/lumina_db
REDIS_URL=redis://redis:6379

# Service URLs (using Docker network names)
EXTRACTION_SERVICE_URL=http://extraction-service:8001
QUERY_SERVICE_URL=http://query-service:8002

# Application Configuration
PYTHONPATH=/app
EXPORTS_BUCKET_NAME=lumina-exports-bucket

# LLM Configurations (loaded from root .env)
NVIDIA_API_KEY=$NVIDIA_API_KEY
NVIDIA_EMBED_API_KEY=$NVIDIA_API_KEY
NVIDIA_RERANK_API_KEY=$NVIDIA_API_KEY
NVIDIA_NIM_API_KEY=$NVIDIA_API_KEY

# Google Gemini API Key (loaded from root .env)
GOOGLE_GEMINI_API_KEY=$GOOGLE_GEMINI_API_KEY

# LLM Models
GRAPH_LLM_MODEL="nvidia/llama-3.1-nemotron-nano-8b-v1"

# Neo4j Configuration (optional)
NEO4J_URL=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
EOF
    
    echo -e "${GREEN}✅ Created .env.personal with API keys from root .env${NC}"
}

# Deploy to instance
deploy_application() {
    echo -e "${BLUE}📦 Deploying application...${NC}"
    
    # Create files
    create_docker_compose_personal
    create_env_file_personal
    
    # Copy files to instance
    echo -e "${YELLOW}📁 Copying files to instance...${NC}"
    scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no docker-compose-backend-personal.yml ec2-user@$PUBLIC_IP:/home/ec2-user/docker-compose-backend.yml
    scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no .env.personal ec2-user@$PUBLIC_IP:/home/ec2-user/.env
    
    # Copy application code
    echo -e "${YELLOW}📁 Copying application code...${NC}"
    scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no -r lumina-backend ec2-user@$PUBLIC_IP:/home/ec2-user/ || echo "Code already exists"
    
    # Deploy on instance
    echo -e "${YELLOW}🚀 Starting services on instance...${NC}"
    ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
        # Stop any existing containers
        docker compose -f docker-compose-backend.yml down 2>/dev/null || true
        
        # Start services with proper networking
        docker compose -f docker-compose-backend.yml up -d --build
        
                
        # Wait for services to be ready
        echo "⏳ Waiting for services to start..."
        sleep 45
        
        # Test service connectivity
        echo "🧪 Testing service connectivity..."
        curl -s http://localhost:8000/ > /dev/null && echo "✅ API Service: OK" || echo "❌ API Service: Failed"
        curl -s http://localhost:8001/health > /dev/null && echo "✅ Extraction Service: OK" || echo "❌ Extraction Service: Failed"
        curl -s http://localhost:8002/health > /dev/null && echo "✅ Query Service: OK" || echo "❌ Query Service: Failed"
ENDSSH
    
    echo -e "${GREEN}✅ Deployment completed${NC}"
}

# Test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing deployment...${NC}"
    
    # Wait for services to start
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 30
    
    # Test health endpoint
    if curl -s --max-time 10 "http://$PUBLIC_IP:8000/" > /dev/null; then
        echo -e "${GREEN}✅ Backend API is responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend API not ready yet (may need more time)${NC}"
    fi
}

# Main execution
main() {
    deploy_application
    test_deployment
    
    echo -e "${GREEN}🎉 Deployment to personal AWS instance completed!${NC}"
    echo -e "${BLUE}📋 Backend endpoint: http://$PUBLIC_IP:8000${NC}"
    echo -e "${GREEN}✅ API keys automatically configured from root .env file${NC}"
    echo
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "   1. Wait 2-3 minutes for services to fully start"
    echo -e "   2. Test: curl http://$PUBLIC_IP:8000/"
    echo -e "   3. Deploy frontend: ./manage-lumina.sh → Option 3"
    echo
    echo -e "${YELLOW}💰 Remember to stop the instance when not in use to save costs${NC}"
    echo -e "   ./manage-lumina.sh → Option 5: Pause System"
}

main