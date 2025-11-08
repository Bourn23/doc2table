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
      - exports_data:/data/exports
    environment:
      - PYTHONPATH=/app
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://lumina:lumina_secure_password_2024@postgres:5432/lumina_db
      # Use OpenAI or other API instead of NIM for personal deployment
      - OPENAI_API_KEY=${OPENAI_API_KEY:-your_openai_key_here}
      - LLM_PROVIDER=openai
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
      - exports_data:/data/exports
    environment:
      - PYTHONPATH=/app
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql+asyncpg://lumina:lumina_secure_password_2024@postgres:5432/lumina_db
      - OPENAI_API_KEY=${OPENAI_API_KEY:-your_openai_key_here}
      - LLM_PROVIDER=openai
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
      - OPENAI_API_KEY=${OPENAI_API_KEY:-your_openai_key_here}
      - LLM_PROVIDER=openai
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
  exports_data:
EOF
}

# Create environment file for personal AWS
create_env_file_personal() {
    cat > .env.personal << 'EOF'
# Database Configuration
POSTGRES_PASSWORD=lumina_secure_password_2024
DATABASE_URL=postgresql+asyncpg://lumina:lumina_secure_password_2024@postgres:5432/lumina_db
REDIS_URL=redis://redis:6379

# Service URLs (using Docker network names)
EXTRACTION_SERVICE_URL=http://extraction-service:8001
QUERY_SERVICE_URL=http://query-service:8002

# OpenAI Configuration (replace NIM)
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Google API Key (optional)
GOOGLE_GEMINI_API_KEY=your_google_api_key_here

# Application Configuration
PYTHONPATH=/app
EXPORTS_BUCKET_NAME=lumina-exports-bucket

# Neo4j Configuration (optional)
NEO4J_URL=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
GRAPH_LLM_MODEL=gpt-3.5-turbo
EOF
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
    echo -e "${YELLOW}💡 Important: Update your .env file with your API keys:${NC}"
    echo -e "   - OPENAI_API_KEY (for LLM functionality)"
    echo -e "   - GOOGLE_GEMINI_API_KEY (optional)"
    echo -e "${YELLOW}💡 SSH to instance: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP${NC}"
    echo -e "${YELLOW}💰 Remember to stop the instance when not in use to save costs${NC}"
}

main