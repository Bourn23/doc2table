#!/bin/bash

# Fix .env.production to use actual backend URL before building
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing .env.production for Frontend Build${NC}"

# Load backend instance info
if [ -f "backend-instance-personal.env" ]; then
    source backend-instance-personal.env
elif [ -f "backend-instance.env" ]; then
    source backend-instance.env
else
    echo -e "${RED}❌ Backend instance info not found${NC}"
    echo -e "${YELLOW}💡 Deploy backend first${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"

# Check if .env.production exists
ENV_FILE="lumina-frontend-async/.env.production"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ $ENV_FILE not found${NC}"
    exit 1
fi

# Extract backend host and port for WebSocket
BACKEND_HOST=$(echo $BACKEND_ENDPOINT_URL | sed 's|http://||' | sed 's|:.*||')
BACKEND_PORT=$(echo $BACKEND_ENDPOINT_URL | sed 's|.*:||')

# Backup original file
cp "$ENV_FILE" "$ENV_FILE.bak"

# Update .env.production with actual backend URLs
cat > "$ENV_FILE" << EOF
VITE_API_BASE_URL=$BACKEND_ENDPOINT_URL
VITE_WS_BASE_URL=ws://$BACKEND_HOST:$BACKEND_PORT
EOF

echo -e "${GREEN}✅ Updated $ENV_FILE${NC}"
echo -e "${YELLOW}   VITE_API_BASE_URL=$BACKEND_ENDPOINT_URL${NC}"
echo -e "${YELLOW}   VITE_WS_BASE_URL=ws://$BACKEND_HOST:$BACKEND_PORT${NC}"
echo
echo -e "${GREEN}🎉 .env.production is now configured correctly!${NC}"
echo -e "${YELLOW}💡 The frontend build will now use the correct backend URL${NC}"
