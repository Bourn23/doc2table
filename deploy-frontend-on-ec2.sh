#!/bin/bash

# Deploy frontend on the same EC2 instance as backend (simplest option)
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Frontend on EC2 Instance${NC}"

# Check if backend is deployed
if [ ! -f "backend-instance-personal.env" ]; then
    echo -e "${RED}❌ backend-instance-personal.env not found${NC}"
    echo -e "${YELLOW}💡 Deploy backend first${NC}"
    exit 1
fi

source backend-instance-personal.env

echo -e "${YELLOW}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"

# Update frontend configuration locally
echo -e "${BLUE}🔧 Configuring frontend...${NC}"
cd lumina-frontend-async

cat > .env << EOF
# Lumina Frontend Environment Variables
VITE_API_BASE_URL=$BACKEND_ENDPOINT_URL
VITE_DEBUG=false
EOF

cd ..

# Copy frontend source to EC2 (will build there)
echo -e "${BLUE}📦 Copying frontend source to EC2...${NC}"
# Create zip to speed up transfer
zip -r frontend-source.zip lumina-frontend-async -x "lumina-frontend-async/node_modules/*" "lumina-frontend-async/dist/*" "lumina-frontend-async/.git/*"
scp -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no frontend-source.zip ec2-user@$PUBLIC_IP:/home/ec2-user/
rm frontend-source.zip

# Build frontend and setup Nginx on EC2
echo -e "${BLUE}🔧 Building frontend on EC2 and setting up Nginx...${NC}"
ssh -i ${KEY_NAME}.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
    # Extract frontend source
    echo "📦 Extracting frontend source..."
    unzip -o frontend-source.zip
    cd lumina-frontend-async
    
    # Install Node.js if not present (Amazon Linux 2 compatible)
    if ! command -v node &> /dev/null; then
        echo "📦 Installing Node.js..."
        # Use NVM with Node 24 (compatible with Amazon Linux 2 glibc)
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
        nvm install 24
        nvm use 24
        echo "✅ Node.js installed: $(node --version)"
    fi
    
    # Ensure Node.js is available
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    nvm use 16 2>/dev/null || true
    
    # Install dependencies and build
    echo "📦 Installing npm dependencies..."
    npm install
    
    echo "🔨 Building frontend..."
    npm run build
    
    # Move built files to frontend directory
    cd ..
    rm -rf frontend
    mv lumina-frontend-async/dist frontend
    
    echo "✅ Frontend built successfully"
    
    # Install Nginx using Amazon Linux Extras
    sudo amazon-linux-extras install -y nginx1
    
    # Create Nginx config
    sudo tee /etc/nginx/conf.d/lumina.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /home/ec2-user/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
EOF
    
    # Start Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    echo "✅ Nginx configured and started"
ENDSSH

# Update security group to allow HTTP
echo -e "${BLUE}🔒 Updating security group for HTTP...${NC}"
SECURITY_GROUP_ID=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 2>/dev/null || echo "Port 80 already open"

# Update frontend URL
FRONTEND_URL="http://$PUBLIC_IP"

# Save frontend info
cat >> backend-instance-personal.env << EOF
FRONTEND_URL=$FRONTEND_URL
FRONTEND_TYPE=ec2-nginx
EOF

echo -e "${GREEN}🎉 Frontend deployed on EC2!${NC}"
echo -e "${BLUE}📋 Frontend URL: $FRONTEND_URL${NC}"
echo -e "${BLUE}📋 Backend API: $BACKEND_ENDPOINT_URL${NC}"
echo -e "${YELLOW}💡 Open your browser and visit: $FRONTEND_URL${NC}"
echo -e "${YELLOW}💰 Cost: $0 (uses existing EC2 instance)${NC}"