#!/bin/bash

# Deploy existing frontend build to S3 (no rebuild needed)
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Existing Frontend Build to S3${NC}"

# Check if backend is deployed
if [ ! -f "backend-instance-personal.env" ]; then
    echo -e "${RED}❌ backend-instance-personal.env not found${NC}"
    exit 1
fi

source backend-instance-personal.env

# Check if dist folder exists
if [ ! -d "lumina-frontend-async/dist" ]; then
    echo -e "${RED}❌ lumina-frontend-async/dist folder not found${NC}"
    echo -e "${YELLOW}💡 You need to build the frontend first${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"

# Use existing S3 bucket or create new one
TIMESTAMP=$(date +%s)
S3_BUCKET="lumina-frontend-${TIMESTAMP}"
REGION=${REGION:-us-east-1}

echo -e "${YELLOW}📋 S3 Bucket: $S3_BUCKET${NC}"

# Create S3 bucket
echo -e "${BLUE}🪣 Creating S3 bucket...${NC}"
if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket $S3_BUCKET --region $REGION
else
    aws s3api create-bucket --bucket $S3_BUCKET --region $REGION --create-bucket-configuration LocationConstraint=$REGION
fi

# Disable public access block
echo -e "${BLUE}🔓 Disabling public access block...${NC}"
aws s3api put-public-access-block \
    --bucket $S3_BUCKET \
    --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Configure bucket for static website hosting
echo -e "${BLUE}🌐 Configuring static website hosting...${NC}"
aws s3 website s3://$S3_BUCKET/ --index-document index.html --error-document index.html

# Set bucket policy for public access
echo -e "${BLUE}🔓 Setting public access policy...${NC}"
cat > bucket-policy-temp.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$S3_BUCKET/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $S3_BUCKET --policy file://bucket-policy-temp.json
rm bucket-policy-temp.json

# Deploy existing dist folder to S3
echo -e "${BLUE}☁️ Deploying existing build to S3...${NC}"
aws s3 sync lumina-frontend-async/dist/ s3://$S3_BUCKET --delete

# Get website URL
FRONTEND_URL="http://$S3_BUCKET.s3-website-$REGION.amazonaws.com"

# Save frontend info
cat >> backend-instance-personal.env << EOF
FRONTEND_URL=$FRONTEND_URL
S3_BUCKET=$S3_BUCKET
EOF

echo -e "${GREEN}🎉 Frontend deployed successfully!${NC}"
echo -e "${BLUE}📋 Frontend URL: $FRONTEND_URL${NC}"
echo -e "${BLUE}📋 Backend URL: $BACKEND_ENDPOINT_URL${NC}"
echo -e "${YELLOW}⚠️  Note: Frontend is using old build (may have localhost URLs)${NC}"
echo -e "${YELLOW}💡 To fix URLs, run: ./fix-websocket-polling.sh${NC}"
echo -e "${YELLOW}💰 Cost: ~$0.50/month for S3 hosting${NC}"