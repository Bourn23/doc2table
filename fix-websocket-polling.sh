#!/bin/bash

# Fix WebSocket and Polling URLs in deployed frontend
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Fixing WebSocket and Polling URLs${NC}"

# Load backend instance info
if [ -f "backend-instance-personal.env" ]; then
    source backend-instance-personal.env
elif [ -f "backend-instance.env" ]; then
    source backend-instance.env
else
    echo -e "${RED}❌ backend-instance.env or backend-instance-personal.env not found${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"

# Check if frontend is deployed
if [ -z "$FRONTEND_URL" ] || [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}❌ Frontend not deployed yet${NC}"
    echo -e "${YELLOW}💡 Deploy frontend first (option 2 in manage-personal.sh)${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 S3 Bucket: $S3_BUCKET${NC}"
echo -e "${YELLOW}📋 Frontend URL: $FRONTEND_URL${NC}"

# Download current frontend files
echo -e "${BLUE}📥 Downloading current frontend files...${NC}"
mkdir -p temp-websocket-fix
aws s3 sync s3://$S3_BUCKET/ temp-websocket-fix/

cd temp-websocket-fix

# Find JavaScript files
MAIN_JS_FILE=$(find assets -name "index-*.js" | head -1)
JOB_MANAGER_JS_FILE=$(find assets -name "jobManager-*.js" | head -1)

echo -e "${YELLOW}📋 Main JS file: $MAIN_JS_FILE${NC}"
echo -e "${YELLOW}📋 Job Manager JS file: $JOB_MANAGER_JS_FILE${NC}"

# Fix WebSocket URL in jobManager file
if [ -n "$JOB_MANAGER_JS_FILE" ]; then
    echo -e "${BLUE}🔧 Fixing WebSocket URL in $JOB_MANAGER_JS_FILE${NC}"
    
    # Replace WebSocket URL patterns
    # Fix: window.location.host -> backend host
    BACKEND_HOST=$(echo $BACKEND_ENDPOINT_URL | sed 's|http://||' | sed 's|:.*||')
    BACKEND_PORT=$(echo $BACKEND_ENDPOINT_URL | sed 's|.*:||')
    
    # Replace WebSocket connection patterns
    sed -i.bak "s|window\.location\.host|\"$BACKEND_HOST:$BACKEND_PORT\"|g" "$JOB_MANAGER_JS_FILE"
    
    # Fix polling URL - replace relative paths with full backend URL
    sed -i.bak "s|api/jobs/|$BACKEND_ENDPOINT_URL/jobs/|g" "$JOB_MANAGER_JS_FILE"
    
    echo -e "${GREEN}✅ Updated WebSocket and polling URLs in $JOB_MANAGER_JS_FILE${NC}"
    
    # Upload the updated file back to S3
    echo -e "${BLUE}☁️ Uploading updated jobManager file to S3...${NC}"
    aws s3 cp "$JOB_MANAGER_JS_FILE" "s3://$S3_BUCKET/$JOB_MANAGER_JS_FILE"
fi

# Also ensure main JS file has correct API URL
if [ -n "$MAIN_JS_FILE" ]; then
    echo -e "${BLUE}🔧 Ensuring correct API URL in $MAIN_JS_FILE${NC}"
    
    # Replace localhost:8000 with actual backend URL
    sed -i.bak "s|http://localhost:8000|$BACKEND_ENDPOINT_URL|g" "$MAIN_JS_FILE"
    
    # Fix relative API paths (like /uploads/initiate, /api/*, etc.)
    # These need to be full URLs to the backend
    sed -i.bak "s|/uploads/|$BACKEND_ENDPOINT_URL/uploads/|g" "$MAIN_JS_FILE"
    sed -i.bak "s|/api/|$BACKEND_ENDPOINT_URL/api/|g" "$MAIN_JS_FILE"
    
    # Fix any remaining relative paths that start with /
    # But be careful not to replace asset paths
    sed -i.bak "s|axios\.post(\"/|axios.post(\"$BACKEND_ENDPOINT_URL/|g" "$MAIN_JS_FILE"
    sed -i.bak "s|axios\.get(\"/|axios.get(\"$BACKEND_ENDPOINT_URL/|g" "$MAIN_JS_FILE"
    
    echo -e "${GREEN}✅ Updated API URL in $MAIN_JS_FILE${NC}"
    
    # Upload the updated file back to S3
    echo -e "${BLUE}☁️ Uploading updated main JS file to S3...${NC}"
    aws s3 cp "$MAIN_JS_FILE" "s3://$S3_BUCKET/$MAIN_JS_FILE"
fi

# Clean up
cd ..
rm -rf temp-websocket-fix

echo -e "${GREEN}🎉 WebSocket and polling URLs fixed!${NC}"
echo -e "${BLUE}📋 Frontend URL: $FRONTEND_URL${NC}"
echo -e "${BLUE}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"
echo -e "${YELLOW}💡 Refresh your browser and try uploading a file again${NC}"
echo -e "${YELLOW}💡 WebSocket should now connect to: ws://$BACKEND_HOST:$BACKEND_PORT${NC}"