#!/bin/bash

# Lumina Personal AWS Manager
# Simplified management dashboard for personal AWS deployments

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_banner() {
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║              🌟 LUMINA PERSONAL AWS MANAGER 🌟               ║${NC}"
    echo -e "${PURPLE}║           Simplified Personal Deployment Manager            ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

show_status_summary() {
    echo -e "${BLUE}📊 Quick Status${NC}"
    echo -e "${BLUE}===============${NC}"
    
    # Check if personal AWS is deployed
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${GREEN}✅ Personal AWS Backend: Deployed${NC}"
        
        # Test backend
        if curl -s --max-time 3 "$BACKEND_ENDPOINT_URL/" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend API: Online${NC}"
        else
            echo -e "${RED}❌ Backend API: Offline${NC}"
        fi
        
        # Test frontend if exists
        if [ -n "$FRONTEND_URL" ]; then
            if curl -s --max-time 3 "$FRONTEND_URL" > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Frontend: Online${NC}"
            else
                echo -e "${RED}❌ Frontend: Offline${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  No personal deployment found${NC}"
        echo -e "${BLUE}💡 Use option 1 to deploy backend${NC}"
    fi
    
    # Check for NIM deployment
    if [ -f "nim-endpoint.env" ]; then
        source nim-endpoint.env
        if curl -s --max-time 3 "$NIM_ENDPOINT_URL/v1/health/ready" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ NIM Models: Online${NC}"
        else
            echo -e "${YELLOW}⚠️  NIM Models: Offline${NC}"
        fi
    fi
    
    echo
}

show_menu() {
    echo -e "${CYAN}🎯 Main Menu${NC}"
    echo -e "${CYAN}============${NC}"
    echo -e "${GREEN}1.${NC} 🤖 Deploy NIM Models"
    echo -e "${GREEN}2.${NC} 🏗️  Deploy Backend"
    echo -e "${GREEN}3.${NC} 🌐 Deploy Frontend"
    echo
    echo -e "${YELLOW}4.${NC} 📊 Show System Status"
    echo -e "${YELLOW}5.${NC} ⏸️  Pause System"
    echo -e "${YELLOW}6.${NC} ▶️  Resume System"
    echo -e "${YELLOW}7.${NC} 🔄 Restart Docker Services (Backend)"
    echo
    echo -e "${BLUE}8.${NC} 🧪 Test Endpoints"
    echo -e "${BLUE}9.${NC} 📋 Show Deployment Info"
    echo -e "${BLUE}10.${NC} 📜 View Docker Logs (Backend)"
    echo -e "${BLUE}11.${NC} 🔧 Fix Frontend Issues"
    echo
    echo -e "${RED}12.${NC} 🧹 Clean Up All Resources"
    echo
    echo -e "${PURPLE}0.${NC} 🚪 Exit"
    echo
}

deploy_personal_backend() {
    echo -e "${YELLOW}🏗️  Deploying Personal AWS Backend${NC}"
    echo -e "${YELLOW}Using t3.medium instance (~$30/month)${NC}"
    echo
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "deploy-backend-personal-aws.sh" ]; then
            ./deploy-backend-personal-aws.sh
            echo
            read -p "Deploy application to instance? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ./deploy-to-existing-backend-personal.sh
            fi
        else
            echo -e "${RED}❌ deploy-backend-personal-aws.sh not found${NC}"
        fi
    fi
    echo
    read -p "Press Enter to continue..."
}

deploy_personal_frontend() {
    echo -e "${YELLOW}🌐 Deploying Personal AWS Frontend${NC}"
    echo
    
    # Check if backend is deployed
    if [ ! -f "backend-instance-personal.env" ]; then
        echo -e "${RED}❌ No personal backend found${NC}"
        echo -e "${YELLOW}💡 Deploy backend first (option 1)${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    # Check if frontend build exists
    if [ ! -d "lumina-frontend-async/dist" ]; then
        echo -e "${YELLOW}⚠️  Frontend build not found${NC}"
        echo -e "${YELLOW}📁 Expected location: lumina-frontend-async/dist${NC}"
        echo
        echo -e "${BLUE}Options:${NC}"
        echo -e "  1. Build frontend now (requires Node.js)"
        echo -e "  2. Copy pre-built dist folder here"
        echo -e "  3. Cancel and build manually"
        echo
        read -p "Select option (1-3): " build_option
        echo
        
        case $build_option in
            1)
                if [ -d "lumina-frontend-async" ]; then
                    echo -e "${BLUE}Building frontend...${NC}"
                    
                    # Check Node.js version
                    NODE_VERSION=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1)
                    
                    if [ -z "$NODE_VERSION" ]; then
                        echo -e "${RED}❌ Node.js not found${NC}"
                        echo -e "${YELLOW}💡 Install Node.js 18+ or use nvm${NC}"
                        read -p "Press Enter to continue..."
                        return
                    fi
                    
                    if [ "$NODE_VERSION" -lt 18 ]; then
                        echo -e "${YELLOW}⚠️  Current Node.js version: v$NODE_VERSION (requires v18+)${NC}"
                        
                        # Check if nvm is available
                        if [ -s "$HOME/.nvm/nvm.sh" ]; then
                            echo -e "${BLUE}Found nvm, switching to Node.js 24...${NC}"
                            source "$HOME/.nvm/nvm.sh"
                            
                            # Check if Node 24 is installed
                            if nvm ls 24 >/dev/null 2>&1; then
                                nvm use 24
                            else
                                echo -e "${YELLOW}Installing Node.js 24...${NC}"
                                nvm install 24
                                nvm use 24
                            fi
                            
                            echo -e "${GREEN}✅ Now using Node.js $(node -v)${NC}"
                        else
                            echo -e "${RED}❌ nvm not found${NC}"
                            echo -e "${YELLOW}💡 Install nvm or upgrade Node.js manually:${NC}"
                            echo -e "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
                            echo -e "   Then run: nvm install 24 && nvm use 24"
                            read -p "Press Enter to continue..."
                            return
                        fi
                    else
                        echo -e "${GREEN}✅ Node.js version: v$NODE_VERSION${NC}"
                    fi
                    
                    # Fix .env.production before building
                    echo -e "${BLUE}Configuring environment for production...${NC}"
                    if [ -f "fix-env-production.sh" ]; then
                        ./fix-env-production.sh
                    else
                        echo -e "${YELLOW}⚠️  fix-env-production.sh not found, skipping env fix${NC}"
                    fi
                    
                    cd lumina-frontend-async
                    
                    # Check if node_modules exists
                    if [ ! -d "node_modules" ]; then
                        echo -e "${YELLOW}Installing dependencies...${NC}"
                        npm install
                    fi
                    
                    # Build
                    echo -e "${YELLOW}Building production bundle...${NC}"
                    npm run build
                    cd ..
                    
                    if [ -d "lumina-frontend-async/dist" ]; then
                        echo -e "${GREEN}✅ Frontend built successfully${NC}"
                    else
                        echo -e "${RED}❌ Build failed${NC}"
                        read -p "Press Enter to continue..."
                        return
                    fi
                else
                    echo -e "${RED}❌ lumina-frontend-async folder not found${NC}"
                    echo -e "${YELLOW}💡 Make sure the frontend code is in this directory${NC}"
                    read -p "Press Enter to continue..."
                    return
                fi
                ;;
            2)
                echo -e "${YELLOW}💡 Copy your pre-built dist folder to: lumina-frontend-async/dist${NC}"
                echo -e "${YELLOW}Then run this option again${NC}"
                read -p "Press Enter to continue..."
                return
                ;;
            3)
                echo -e "${YELLOW}Build manually with:${NC}"
                echo -e "  cd lumina-frontend-async"
                echo -e "  npm install"
                echo -e "  npm run build"
                read -p "Press Enter to continue..."
                return
                ;;
            *)
                echo -e "${RED}❌ Invalid option${NC}"
                read -p "Press Enter to continue..."
                return
                ;;
        esac
        echo
    fi
    
    echo -e "${BLUE}Choose deployment option:${NC}"
    echo -e "  1. 📦 Deploy to S3 (recommended; quick)"
    echo -e "  2. 🖥️  Deploy on EC2 with Nginx (no extra cost)"
    echo
    read -p "Select option (1-2): " frontend_type
    echo
    
    case $frontend_type in
        1)
            echo -e "${BLUE}Deploying to S3...${NC}"
            if [ -f "deploy-existing-frontend-to-s3.sh" ]; then
                ./deploy-existing-frontend-to-s3.sh
                
                if [ $? -eq 0 ]; then
                    echo
                    echo -e "${YELLOW}Applying fixes...${NC}"
                    [ -f "fix-websocket-polling.sh" ] && ./fix-websocket-polling.sh 2>/dev/null
                    [ -f "fix-download-button.sh" ] && ./fix-download-button.sh 2>/dev/null
                    echo -e "${GREEN}✅ Frontend deployment complete${NC}"
                fi
            else
                echo -e "${RED}❌ deploy-existing-frontend-to-s3.sh not found${NC}"
            fi
            ;;
        2)
            echo -e "${BLUE}Deploying on EC2 with Nginx...${NC}"
            if [ -f "deploy-frontend-on-ec2.sh" ]; then
                ./deploy-frontend-on-ec2.sh
            else
                echo -e "${RED}❌ deploy-frontend-on-ec2.sh not found${NC}"
            fi
            ;;
        *)
            echo -e "${RED}❌ Invalid option${NC}"
            ;;
    esac
    echo
    read -p "Press Enter to continue..."
}


show_system_status() {
    echo -e "${BLUE}📊 Detailed System Status${NC}"
    echo
    
    if [ -f "status-system.sh" ]; then
        ./status-system.sh
    else
        # Manual status check
        if [ -f "backend-instance-personal.env" ]; then
            source backend-instance-personal.env
            echo -e "${GREEN}Backend Instance:${NC}"
            echo -e "  Instance ID: $INSTANCE_ID"
            echo -e "  Public IP: $PUBLIC_IP"
            echo -e "  Backend URL: $BACKEND_ENDPOINT_URL"
            echo -e "  Frontend URL: $FRONTEND_URL"
            echo
            
            # Check instance state
            if command -v aws &> /dev/null; then
                STATE=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null)
                echo -e "  Instance State: $STATE"
            fi
        else
            echo -e "${YELLOW}No personal deployment found${NC}"
        fi
        
        if [ -f "nim-endpoint.env" ]; then
            source nim-endpoint.env
            echo
            echo -e "${GREEN}NIM Deployment:${NC}"
            echo -e "  NIM Endpoint: $NIM_ENDPOINT_URL"
        fi
    fi
    echo
    read -p "Press Enter to continue..."
}

deploy_nim_only() {
    echo -e "${YELLOW}🤖 Deploying NIM Models${NC}"
    echo -e "${YELLOW}This will deploy NVIDIA NIM on EKS${NC}"
    echo -e "${YELLOW}Estimated time: 15-20 minutes${NC}"
    echo -e "${YELLOW}Cost: ~$1.50/hour${NC}"
    echo
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "deploy-model.sh" ]; then
            ./deploy-model.sh
        else
            echo -e "${RED}❌ deploy-model.sh not found${NC}"
        fi
    fi
    echo
    read -p "Press Enter to continue..."
}

pause_system() {
    echo -e "${YELLOW}⏸️  Pausing System${NC}"
    echo
    
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${YELLOW}This will stop your EC2 instance to save costs${NC}"
        echo -e "${YELLOW}Instance ID: $INSTANCE_ID${NC}"
        echo
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v aws &> /dev/null; then
                aws ec2 stop-instances --instance-ids $INSTANCE_ID
                echo -e "${GREEN}✅ Instance stopped${NC}"
            else
                echo -e "${RED}❌ AWS CLI not found${NC}"
            fi
        fi
    elif [ -f "pause-system.sh" ]; then
        ./pause-system.sh
    else
        echo -e "${YELLOW}No system to pause${NC}"
    fi
    echo
    read -p "Press Enter to continue..."
}

resume_system() {
    echo -e "${GREEN}▶️  Resuming System${NC}"
    echo
    
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${YELLOW}This will start your EC2 instance${NC}"
        echo -e "${YELLOW}Instance ID: $INSTANCE_ID${NC}"
        echo
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v aws &> /dev/null; then
                aws ec2 start-instances --instance-ids $INSTANCE_ID
                echo -e "${GREEN}✅ Instance starting...${NC}"
                echo -e "${YELLOW}⏳ Waiting for instance to be ready...${NC}"
                aws ec2 wait instance-running --instance-ids $INSTANCE_ID
                
                # Get new IP if it changed
                NEW_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
                echo -e "${GREEN}✅ Instance running at: $NEW_IP${NC}"
                
                if [ "$NEW_IP" != "$PUBLIC_IP" ]; then
                    echo -e "${YELLOW}⚠️  IP address changed from $PUBLIC_IP to $NEW_IP${NC}"
                    echo -e "${YELLOW}💡 You may need to update your frontend configuration${NC}"
                fi
            else
                echo -e "${RED}❌ AWS CLI not found${NC}"
            fi
        fi
    elif [ -f "resume-system.sh" ]; then
        ./resume-system.sh
    else
        echo -e "${YELLOW}No system to resume${NC}"
    fi
    echo
    read -p "Press Enter to continue..."
}

test_endpoints() {
    echo -e "${BLUE}🧪 Testing Endpoints${NC}"
    echo
    
    # Test backend
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${YELLOW}Testing backend: $BACKEND_ENDPOINT_URL${NC}"
        
        if curl -s --max-time 5 "$BACKEND_ENDPOINT_URL/" > /dev/null; then
            echo -e "${GREEN}✅ Backend API: Responding${NC}"
            
            # Test upload endpoint
            if curl -s -X POST "$BACKEND_ENDPOINT_URL/uploads/initiate" \
                -H "Content-Type: application/json" \
                -d '{"filenames": ["test.txt"]}' | grep -q "session_id"; then
                echo -e "${GREEN}✅ Upload endpoint: OK${NC}"
            else
                echo -e "${RED}❌ Upload endpoint: Failed${NC}"
            fi
        else
            echo -e "${RED}❌ Backend API: Not responding${NC}"
        fi
        
        # Test frontend
        if [ -n "$FRONTEND_URL" ]; then
            echo
            echo -e "${YELLOW}Testing frontend: $FRONTEND_URL${NC}"
            if curl -s --max-time 5 "$FRONTEND_URL" > /dev/null; then
                echo -e "${GREEN}✅ Frontend: Accessible${NC}"
            else
                echo -e "${RED}❌ Frontend: Not accessible${NC}"
            fi
        fi
    fi
    
    # Test NIM
    if [ -f "nim-endpoint.env" ]; then
        source nim-endpoint.env
        echo
        echo -e "${YELLOW}Testing NIM: $NIM_ENDPOINT_URL${NC}"
        if curl -s --max-time 10 "$NIM_ENDPOINT_URL/v1/health/ready" > /dev/null; then
            echo -e "${GREEN}✅ NIM Health: OK${NC}"
        else
            echo -e "${RED}❌ NIM: Not responding${NC}"
        fi
    fi
    
    echo
    read -p "Press Enter to continue..."
}

show_deployment_info() {
    echo -e "${BLUE}📋 Deployment Information${NC}"
    echo
    
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${GREEN}🖥️  Backend Instance:${NC}"
        echo -e "   Instance ID: $INSTANCE_ID"
        echo -e "   Instance Type: ${INSTANCE_TYPE:-t3.medium}"
        echo -e "   Public IP: $PUBLIC_IP"
        echo -e "   Region: ${REGION:-us-east-1}"
        echo -e "   Backend URL: $BACKEND_ENDPOINT_URL"
        echo -e "   SSH: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
        echo
        
        if [ -n "$FRONTEND_URL" ]; then
            echo -e "${GREEN}🌐 Frontend:${NC}"
            echo -e "   URL: $FRONTEND_URL"
            if [ -n "$S3_BUCKET" ]; then
                echo -e "   S3 Bucket: $S3_BUCKET"
            fi
            echo
        fi
        
        echo -e "${GREEN}💰 Estimated Costs:${NC}"
        echo -e "   EC2 (t3.medium): ~$30/month"
        echo -e "   S3 Hosting: ~$0.50/month"
        echo -e "   Total: ~$30-31/month"
    else
        echo -e "${YELLOW}No personal deployment found${NC}"
    fi
    
    if [ -f "nim-endpoint.env" ]; then
        source nim-endpoint.env
        echo
        echo -e "${GREEN}🤖 NIM Deployment:${NC}"
        echo -e "   Endpoint: $NIM_ENDPOINT_URL"
        echo -e "   Cost: ~$1.50/hour when running"
    fi
    
    echo
    read -p "Press Enter to continue..."
}

fix_frontend_issues() {
    echo -e "${YELLOW}🔧 Fixing Frontend Issues${NC}"
    echo
    echo -e "${BLUE}Available fixes:${NC}"
    echo -e "  1. 🔗 Fix WebSocket and Polling URLs"
    echo -e "  2. 📥 Fix Download Button"
    echo -e "  3. 🌐 Fix All API URLs (Comprehensive)"
    echo -e "  4. ⚙️  Fix .env.production and Rebuild"
    echo -e "  5. 🔄 Fix All Issues"
    echo
    read -p "Select option (1-5): " fix_type
    echo
    
    case $fix_type in
        1)
            if [ -f "fix-websocket-polling.sh" ]; then
                ./fix-websocket-polling.sh
            else
                echo -e "${RED}❌ fix-websocket-polling.sh not found${NC}"
            fi
            ;;
        2)
            if [ -f "fix-download-button.sh" ]; then
                ./fix-download-button.sh
            else
                echo -e "${RED}❌ fix-download-button.sh not found${NC}"
            fi
            ;;
        3)
            if [ -f "fix-all-api-urls.sh" ]; then
                ./fix-all-api-urls.sh
            else
                echo -e "${RED}❌ fix-all-api-urls.sh not found${NC}"
            fi
            ;;
        4)
            if [ -f "fix-env-production.sh" ]; then
                ./fix-env-production.sh
                echo
                echo -e "${YELLOW}💡 .env.production has been updated${NC}"
                read -p "Rebuild and redeploy frontend now? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    if [ -d "lumina-frontend-async" ]; then
                        cd lumina-frontend-async
                        npm run build
                        cd ..
                        echo -e "${GREEN}✅ Frontend rebuilt${NC}"
                        
                        # Redeploy to S3
                        if [ -f "deploy-existing-frontend-to-s3.sh" ]; then
                            echo -e "${BLUE}Redeploying to S3...${NC}"
                            # Just sync the new build, don't create new bucket
                            source backend-instance-personal.env
                            aws s3 sync lumina-frontend-async/dist/ s3://$S3_BUCKET --delete
                            echo -e "${GREEN}✅ Frontend redeployed${NC}"
                        fi
                    fi
                fi
            else
                echo -e "${RED}❌ fix-env-production.sh not found${NC}"
            fi
            ;;
        5)
            echo -e "${BLUE}Applying all fixes...${NC}"
            
            # First try to fix at source (rebuild with correct env)
            if [ -f "fix-env-production.sh" ] && [ -d "lumina-frontend-async" ]; then
                echo -e "${BLUE}1. Fixing .env.production...${NC}"
                ./fix-env-production.sh
                
                echo -e "${BLUE}2. Rebuilding frontend...${NC}"
                cd lumina-frontend-async
                npm run build
                cd ..
                
                echo -e "${BLUE}3. Redeploying to S3...${NC}"
                if [ -f "backend-instance-personal.env" ]; then
                    source backend-instance-personal.env
                    aws s3 sync lumina-frontend-async/dist/ s3://$S3_BUCKET --delete
                fi
                
                echo -e "${GREEN}✅ All fixes applied via rebuild${NC}"
            else
                # Fallback to post-deployment fixes
                echo -e "${YELLOW}Applying post-deployment fixes...${NC}"
                if [ -f "fix-all-api-urls.sh" ]; then
                    ./fix-all-api-urls.sh
                else
                    [ -f "fix-websocket-polling.sh" ] && ./fix-websocket-polling.sh
                    [ -f "fix-download-button.sh" ] && ./fix-download-button.sh
                fi
                echo -e "${GREEN}✅ All fixes applied${NC}"
            fi
            ;;
        *)
            echo -e "${RED}❌ Invalid option${NC}"
            ;;
    esac
    echo
    read -p "Press Enter to continue..."
}

restart_docker_services() {
    echo -e "${YELLOW}🔄 Restart Docker Services${NC}"
    echo
    
    if [ ! -f "backend-instance-personal.env" ]; then
        echo -e "${RED}❌ No personal backend found${NC}"
        echo -e "${YELLOW}💡 Deploy backend first (option 1)${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    source backend-instance-personal.env
    
    echo -e "${YELLOW}This will restart all Docker containers on: $PUBLIC_IP${NC}"
    echo
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Connecting to instance...${NC}"
        
        # Restart docker services
        ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
echo "🔄 Restarting Docker services..."

# Check if docker-compose.yml exists
if [ -f "docker-compose-backend.yml" ]; then
    echo "📦 Stopping containers..."
    docker compose -f docker-compose-backend.yml down
    
    echo "🚀 Starting containers..."
    docker compose -f docker-compose-backend.yml up -d
    
    echo "✅ Docker services restarted"
    
    echo ""
    echo "📊 Container status:"
    docker compose -f docker-compose-backend.yml ps
else
    echo "⚠️  No docker-compose-backend.yml found"
    echo "💡 Checking for running containers..."
    docker ps
fi
ENDSSH
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Docker services restarted successfully${NC}"
        else
            echo -e "${RED}❌ Failed to restart Docker services${NC}"
        fi
    fi
    
    echo
    read -p "Press Enter to continue..."
}

view_docker_logs() {
    echo -e "${BLUE}📜 View Docker Logs${NC}"
    echo
    
    if [ ! -f "backend-instance-personal.env" ]; then
        echo -e "${RED}❌ No personal backend found${NC}"
        echo -e "${YELLOW}💡 Deploy backend first (option 1)${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    source backend-instance-personal.env
    
    echo -e "${BLUE}Select log option:${NC}"
    echo -e "  1. 📋 View all container logs"
    echo -e "  2. 🎯 View specific container logs"
    echo -e "  3. 🔄 Follow logs (live tail)"
    echo
    read -p "Select option (1-3): " log_option
    echo
    
    case $log_option in
        1)
            echo -e "${BLUE}Fetching all container logs...${NC}"
            ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
cd ~/lumina
if [ -f "docker-compose-backend.yml" ]; then
    echo "📊 Container Status:"
    docker compose -f docker-compose-backend.yml ps
    echo ""
    echo "📜 Recent Logs (last 50 lines per container):"
    docker compose -f docker-compose-backend.yml logs --tail=50
else
    echo "📊 Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "📜 Recent Logs (last 50 lines per container):"
    for container in $(docker ps --format "{{.Names}}"); do
        echo ""
        echo "=== $container ==="
        docker logs --tail=50 $container 2>&1
    done
fi
ENDSSH
            ;;
        2)
            echo -e "${YELLOW}Available containers:${NC}"
            ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
cd ~/lumina
if [ -f "docker-compose-backend.yml" ]; then
    docker compose -f docker-compose-backend.yml ps --format "table {{.Service}}\t{{.Status}}"
else
    docker ps --format "table {{.Names}}\t{{.Status}}"
fi
ENDSSH
            echo
            read -p "Enter container/service name: " container_name
            echo
            echo -e "${BLUE}Fetching logs for: $container_name${NC}"
            ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << ENDSSH
cd ~/lumina
if [ -f "docker-compose-backend.yml" ]; then
    docker compose -f docker-compose-backend.yml logs --tail=100 $container_name
else
    docker logs --tail=100 $container_name
fi
ENDSSH
            ;;
        3)
            echo -e "${BLUE}Following logs (Ctrl+C to stop)...${NC}"
            echo -e "${YELLOW}This will stream live logs from all containers${NC}"
            echo
            
            # Get list of containers first
            echo -e "${YELLOW}Available containers:${NC}"
            ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
docker ps --format "  - {{.Names}}"
ENDSSH
            echo
            read -p "Enter container name (or press Enter for all): " follow_container
            echo
            
            if [ -z "$follow_container" ]; then
                echo -e "${BLUE}Following all container logs...${NC}"
                ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
cd ~/lumina
if [ -f "docker-compose-backend.yml" ]; then
    docker compose -f docker-compose-backend.yml logs -f
else
    # Follow logs from all containers
    docker ps -q | xargs -I {} docker logs -f {} 2>&1
fi
ENDSSH
            else
                echo -e "${BLUE}Following logs for: $follow_container${NC}"
                ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << ENDSSH
docker logs -f $follow_container 2>&1
ENDSSH
            fi
            ;;
        *)
            echo -e "${RED}❌ Invalid option${NC}"
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
}

clean_up_resources() {
    echo -e "${RED}🧹 Clean Up All Resources${NC}"
    echo -e "${RED}WARNING: This will delete ALL resources!${NC}"
    echo
    
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${YELLOW}Resources to be deleted:${NC}"
        echo -e "   • EC2 Instance: $INSTANCE_ID"
        [ -n "$S3_BUCKET" ] && echo -e "   • S3 Bucket: $S3_BUCKET"
        echo -e "   • Security Groups"
        echo -e "   • Key Pairs"
        echo
    fi
    
    echo -e "${RED}This action cannot be undone.${NC}"
    read -p "Type 'DELETE' to confirm: " confirm
    
    if [ "$confirm" = "DELETE" ]; then
        echo -e "${RED}Cleaning up resources...${NC}"
        
        if [ -f "backend-instance-personal.env" ] && command -v aws &> /dev/null; then
            source backend-instance-personal.env
            
            # Terminate EC2 instance
            echo -e "${YELLOW}Terminating EC2 instance...${NC}"
            aws ec2 terminate-instances --instance-ids $INSTANCE_ID
            
            # Delete S3 bucket if exists
            if [ -n "$S3_BUCKET" ]; then
                echo -e "${YELLOW}Deleting S3 bucket...${NC}"
                aws s3 rb s3://$S3_BUCKET --force
            fi
            
            echo -e "${GREEN}✅ Resources cleaned up${NC}"
            
            # Remove config files
            rm -f backend-instance-personal.env
            rm -f backend-instance-free-tier.env
        fi
        
        # Clean up NIM if exists
        if [ -f "nim-endpoint.env" ]; then
            echo -e "${YELLOW}Cleaning up NIM deployment...${NC}"
            # Add NIM cleanup commands here if needed
        fi
        
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo -e "${YELLOW}Cleanup cancelled${NC}"
    fi
    echo
    read -p "Press Enter to continue..."
}

clean_up_resources() {
    echo -e "${RED}🧹 Clean Up All Resources${NC}"
    echo -e "${RED}WARNING: This will delete ALL resources!${NC}"
    echo
    
    if [ -f "backend-instance-personal.env" ]; then
        source backend-instance-personal.env
        echo -e "${YELLOW}Resources to be deleted:${NC}"
        echo -e "   • EC2 Instance: $INSTANCE_ID"
        [ -n "$S3_BUCKET" ] && echo -e "   • S3 Bucket: $S3_BUCKET"
        echo -e "   • Security Groups"
        echo -e "   • Key Pairs"
        echo
    fi
    
    echo -e "${RED}This action cannot be undone.${NC}"
    read -p "Type 'DELETE' to confirm: " confirm
    
    if [ "$confirm" = "DELETE" ]; then
        echo -e "${RED}Cleaning up resources...${NC}"
        
        if [ -f "backend-instance-personal.env" ] && command -v aws &> /dev/null; then
            source backend-instance-personal.env
            
            # Terminate EC2 instance
            echo -e "${YELLOW}Terminating EC2 instance...${NC}"
            aws ec2 terminate-instances --instance-ids $INSTANCE_ID
            
            # Delete S3 bucket if exists
            if [ -n "$S3_BUCKET" ]; then
                echo -e "${YELLOW}Deleting S3 bucket...${NC}"
                aws s3 rb s3://$S3_BUCKET --force
            fi
            
            echo -e "${GREEN}✅ Resources cleaned up${NC}"
            
            # Remove config files
            rm -f backend-instance-personal.env
            rm -f backend-instance-free-tier.env
        fi
        
        # Clean up NIM if exists
        if [ -f "nim-endpoint.env" ]; then
            echo -e "${YELLOW}Cleaning up NIM deployment...${NC}"
            # Add NIM cleanup commands here if needed
        fi
        
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo -e "${YELLOW}Cleanup cancelled${NC}"
    fi
    echo
    read -p "Press Enter to continue..."
}

# Main loop
main() {
    while true; do
        show_banner
        show_status_summary
        show_menu
        
        read -p "Select an option (0-12): " choice
        echo
        
        case $choice in
            1) deploy_nim_only ;;
            2) deploy_personal_backend ;;
            3) deploy_personal_frontend ;;
            4) show_system_status ;;
            5) pause_system ;;
            6) resume_system ;;
            7) restart_docker_services ;;
            8) test_endpoints ;;
            9) show_deployment_info ;;
            10) view_docker_logs ;;
            11) fix_frontend_issues ;;
            12) clean_up_resources ;;
            0) 
                echo -e "${GREEN}👋 Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid option. Please try again.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Check if running in interactive mode
if [ -t 0 ]; then
    main
else
    echo "This script requires interactive mode"
    exit 1
fi
