#!/bin/bash

# Fix download button by updating the frontend code
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing Download Button${NC}"

# Load backend instance info
if [ -f "backend-instance-personal.env" ]; then
    source backend-instance-personal.env
elif [ -f "backend-instance.env" ]; then
    source backend-instance.env
else
    echo -e "${RED}❌ Backend instance info not found${NC}"
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
mkdir -p temp-download-fix
aws s3 sync s3://$S3_BUCKET/ temp-download-fix/

cd temp-download-fix

# Find the main JavaScript file
MAIN_JS_FILE=$(find assets -name "index-*.js" | head -1)

if [ -z "$MAIN_JS_FILE" ]; then
    echo -e "${RED}❌ Could not find main JavaScript file${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Found JS file: $MAIN_JS_FILE${NC}"

# Fix the download function
echo -e "${BLUE}🔧 Fixing download button...${NC}"

# The issue is that download URLs use relative paths (/download/...)
# but they should use the full backend URL
# Replace /download/ with the full backend URL

BACKEND_HOST=$(echo $BACKEND_ENDPOINT_URL | sed 's|http://||' | sed 's|:.*||')
BACKEND_PORT=$(echo $BACKEND_ENDPOINT_URL | sed 's|.*:||')

# Fix download URLs to use full backend URL
sed -i.bak "s|/download/|$BACKEND_ENDPOINT_URL/download/|g" "$MAIN_JS_FILE"

echo -e "${GREEN}✅ Updated download URLs to use: $BACKEND_ENDPOINT_URL/download/${NC}"

# Upload the fixed file back to S3
echo -e "${BLUE}☁️ Uploading fixed file to S3...${NC}"
aws s3 cp "$MAIN_JS_FILE" "s3://$S3_BUCKET/$MAIN_JS_FILE"

# Clean up
cd ..
rm -rf temp-download-fix

echo -e "${GREEN}🎉 Download button fixed!${NC}"
echo -e "${YELLOW}💡 Refresh your browser (hard refresh: Cmd+Shift+R or Ctrl+Shift+R)${NC}"
echo -e "${YELLOW}💡 The download button should now work properly${NC}"
