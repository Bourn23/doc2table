#!/bin/bash

# Comprehensive fix for all API URLs in deployed frontend
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing All API URLs in Frontend${NC}"

# Load backend instance info
if [ -f "backend-instance-personal.env" ]; then
    source backend-instance-personal.env
elif [ -f "backend-instance.env" ]; then
    source backend-instance.env
else
    echo -e "${RED}❌ Backend instance info not found${NC}"
    exit 1
fi

# Check if frontend is deployed
if [ -z "$FRONTEND_URL" ] || [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}❌ Frontend not deployed yet${NC}"
    echo -e "${YELLOW}💡 Deploy frontend first (option 2 in manage-personal.sh)${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"
echo -e "${YELLOW}📋 S3 Bucket: $S3_BUCKET${NC}"
echo -e "${YELLOW}📋 Frontend URL: $FRONTEND_URL${NC}"

# Download current frontend files
echo -e "${BLUE}📥 Downloading current frontend files...${NC}"
mkdir -p temp-api-fix
aws s3 sync s3://$S3_BUCKET/ temp-api-fix/

cd temp-api-fix

# Find all JavaScript files
echo -e "${BLUE}🔍 Finding JavaScript files...${NC}"
JS_FILES=$(find assets -name "*.js" 2>/dev/null || echo "")

if [ -z "$JS_FILES" ]; then
    echo -e "${RED}❌ No JavaScript files found${NC}"
    cd ..
    rm -rf temp-api-fix
    exit 1
fi

echo -e "${YELLOW}Found $(echo "$JS_FILES" | wc -l) JavaScript files${NC}"

# Extract backend host and port
BACKEND_HOST=$(echo $BACKEND_ENDPOINT_URL | sed 's|http://||' | sed 's|:.*||')
BACKEND_PORT=$(echo $BACKEND_ENDPOINT_URL | sed 's|.*:||')

# Fix each JavaScript file
for JS_FILE in $JS_FILES; do
    echo -e "${BLUE}🔧 Processing: $JS_FILE${NC}"
    
    # Create backup
    cp "$JS_FILE" "$JS_FILE.bak"
    
    # 1. Replace localhost:8000 with actual backend URL
    sed -i.tmp "s|http://localhost:8000|$BACKEND_ENDPOINT_URL|g" "$JS_FILE"
    
    # 2. Fix WebSocket URLs
    sed -i.tmp "s|ws://localhost:8000|ws://$BACKEND_HOST:$BACKEND_PORT|g" "$JS_FILE"
    sed -i.tmp "s|window\.location\.host|\"$BACKEND_HOST:$BACKEND_PORT\"|g" "$JS_FILE"
    
    # 3. Fix relative API paths - be careful with the order
    # Fix /uploads/ paths
    sed -i.tmp "s|\"/uploads/|\"/uploads/|g" "$JS_FILE"
    sed -i.tmp "s|'/uploads/|'$BACKEND_ENDPOINT_URL/uploads/|g" "$JS_FILE"
    sed -i.tmp "s|\"/uploads/|\"$BACKEND_ENDPOINT_URL/uploads/|g" "$JS_FILE"
    
    # Fix /api/ paths
    sed -i.tmp "s|'/api/|'$BACKEND_ENDPOINT_URL/api/|g" "$JS_FILE"
    sed -i.tmp "s|\"/api/|\"$BACKEND_ENDPOINT_URL/api/|g" "$JS_FILE"
    
    # Fix /download/ paths
    sed -i.tmp "s|'/download/|'$BACKEND_ENDPOINT_URL/download/|g" "$JS_FILE"
    sed -i.tmp "s|\"/download/|\"$BACKEND_ENDPOINT_URL/download/|g" "$JS_FILE"
    
    # Fix /jobs/ paths
    sed -i.tmp "s|'/jobs/|'$BACKEND_ENDPOINT_URL/jobs/|g" "$JS_FILE"
    sed -i.tmp "s|\"/jobs/|\"$BACKEND_ENDPOINT_URL/jobs/|g" "$JS_FILE"
    
    # 4. Fix axios calls with relative paths
    sed -i.tmp "s|axios\.post(\"/|axios.post(\"$BACKEND_ENDPOINT_URL/|g" "$JS_FILE"
    sed -i.tmp "s|axios\.get(\"/|axios.get(\"$BACKEND_ENDPOINT_URL/|g" "$JS_FILE"
    sed -i.tmp "s|axios\.put(\"/|axios.put(\"$BACKEND_ENDPOINT_URL/|g" "$JS_FILE"
    sed -i.tmp "s|axios\.delete(\"/|axios.delete(\"$BACKEND_ENDPOINT_URL/|g" "$JS_FILE"
    
    # Clean up temp files
    rm -f "$JS_FILE.tmp"
    
    # Upload the fixed file back to S3
    echo -e "${BLUE}☁️ Uploading: $JS_FILE${NC}"
    aws s3 cp "$JS_FILE" "s3://$S3_BUCKET/$JS_FILE" --content-type "application/javascript"
done

# Clean up
cd ..
rm -rf temp-api-fix

echo -e "${GREEN}🎉 All API URLs fixed!${NC}"
echo -e "${BLUE}📋 Frontend URL: $FRONTEND_URL${NC}"
echo -e "${BLUE}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"
echo
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "   1. Hard refresh your browser (Cmd+Shift+R or Ctrl+Shift+R)"
echo -e "   2. Clear browser cache if issues persist"
echo -e "   3. Check browser console for any remaining errors"
echo
echo -e "${GREEN}✅ Your frontend should now connect to: $BACKEND_ENDPOINT_URL${NC}"
