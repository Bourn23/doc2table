#!/bin/bash

# AWS Connection Debug Script
# Helps diagnose why AWS connection is failing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 AWS Connection Debug${NC}"
echo -e "${BLUE}======================${NC}"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Load environment variables
echo -e "${YELLOW}📋 Loading .env file...${NC}"
source .env

# Show what we loaded (masked)
echo -e "${BLUE}Loaded credentials:${NC}"
echo -e "   AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:10}...${AWS_ACCESS_KEY_ID: -4}"
echo -e "   AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:0:10}...${AWS_SECRET_ACCESS_KEY: -4}"
echo -e "   AWS_SESSION_TOKEN: $([ -n "$AWS_SESSION_TOKEN" ] && echo "${AWS_SESSION_TOKEN:0:20}...${AWS_SESSION_TOKEN: -4}" || echo "Not set")"
echo -e "   AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
echo

# Check if AWS CLI is installed
echo -e "${YELLOW}🔧 Checking AWS CLI...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not installed${NC}"
    echo -e "${YELLOW}Install with: brew install awscli${NC}"
    exit 1
fi

AWS_VERSION=$(aws --version 2>&1)
echo -e "${GREEN}✅ AWS CLI installed: $AWS_VERSION${NC}"
echo

# Export credentials
echo -e "${YELLOW}🔑 Exporting credentials to environment...${NC}"
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION
[ -n "$AWS_SESSION_TOKEN" ] && export AWS_SESSION_TOKEN

echo -e "${GREEN}✅ Credentials exported${NC}"
echo

# Test 1: Basic AWS call with verbose output
echo -e "${YELLOW}🧪 Test 1: AWS STS Get Caller Identity (verbose)${NC}"
echo -e "${BLUE}Running: aws sts get-caller-identity${NC}"
echo

aws sts get-caller-identity 2>&1
TEST1_EXIT=$?

echo
if [ $TEST1_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Test 1 PASSED${NC}"
else
    echo -e "${RED}❌ Test 1 FAILED (exit code: $TEST1_EXIT)${NC}"
fi
echo

# Test 2: Check credential format
echo -e "${YELLOW}🧪 Test 2: Credential Format Check${NC}"

# Check Access Key ID format (should start with AKIA or ASIA)
if [[ $AWS_ACCESS_KEY_ID =~ ^(AKIA|ASIA) ]]; then
    echo -e "${GREEN}✅ Access Key ID format looks valid${NC}"
else
    echo -e "${YELLOW}⚠️  Access Key ID doesn't start with AKIA or ASIA${NC}"
    echo -e "${YELLOW}   This might be OK for some AWS accounts${NC}"
fi

# Check Secret Access Key length (should be 40 characters)
SECRET_LEN=${#AWS_SECRET_ACCESS_KEY}
if [ $SECRET_LEN -eq 40 ]; then
    echo -e "${GREEN}✅ Secret Access Key length is correct (40 chars)${NC}"
else
    echo -e "${YELLOW}⚠️  Secret Access Key length is $SECRET_LEN (expected 40)${NC}"
fi

# Check if session token is set for temporary credentials
if [[ $AWS_ACCESS_KEY_ID =~ ^ASIA ]]; then
    if [ -n "$AWS_SESSION_TOKEN" ]; then
        echo -e "${GREEN}✅ Session token is set (required for ASIA keys)${NC}"
    else
        echo -e "${RED}❌ Session token is missing (required for ASIA keys)${NC}"
        echo -e "${YELLOW}   ASIA keys are temporary and require a session token${NC}"
    fi
fi

echo

# Test 3: Check AWS configuration files
echo -e "${YELLOW}🧪 Test 3: AWS Configuration Files${NC}"

if [ -f ~/.aws/credentials ]; then
    echo -e "${GREEN}✅ ~/.aws/credentials exists${NC}"
    echo -e "${BLUE}   Profiles found:${NC}"
    grep '^\[' ~/.aws/credentials | sed 's/\[/   - /g' | sed 's/\]//g'
else
    echo -e "${YELLOW}⚠️  ~/.aws/credentials not found${NC}"
fi

if [ -f ~/.aws/config ]; then
    echo -e "${GREEN}✅ ~/.aws/config exists${NC}"
else
    echo -e "${YELLOW}⚠️  ~/.aws/config not found${NC}"
fi

echo

# Test 4: Check network connectivity
echo -e "${YELLOW}🧪 Test 4: Network Connectivity${NC}"
echo -e "${BLUE}Testing connection to AWS STS endpoint...${NC}"

if curl -s --max-time 5 https://sts.amazonaws.com > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Can reach AWS STS endpoint${NC}"
else
    echo -e "${RED}❌ Cannot reach AWS STS endpoint${NC}"
    echo -e "${YELLOW}   Check your internet connection${NC}"
fi

echo

# Test 5: Try with explicit region
echo -e "${YELLOW}🧪 Test 5: Test with Explicit Region${NC}"
echo -e "${BLUE}Running: aws sts get-caller-identity --region $AWS_DEFAULT_REGION${NC}"
echo

aws sts get-caller-identity --region "$AWS_DEFAULT_REGION" 2>&1
TEST5_EXIT=$?

echo
if [ $TEST5_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Test 5 PASSED${NC}"
else
    echo -e "${RED}❌ Test 5 FAILED (exit code: $TEST5_EXIT)${NC}"
fi
echo

# Test 6: Check for common issues
echo -e "${YELLOW}🧪 Test 6: Common Issues Check${NC}"

# Check for whitespace in credentials
if [[ $AWS_ACCESS_KEY_ID =~ [[:space:]] ]]; then
    echo -e "${RED}❌ Access Key ID contains whitespace${NC}"
else
    echo -e "${GREEN}✅ No whitespace in Access Key ID${NC}"
fi

if [[ $AWS_SECRET_ACCESS_KEY =~ [[:space:]] ]]; then
    echo -e "${RED}❌ Secret Access Key contains whitespace${NC}"
else
    echo -e "${GREEN}✅ No whitespace in Secret Access Key${NC}"
fi

# Check if credentials are the example values
if [ "$AWS_ACCESS_KEY_ID" = "AKIAIOSFODNN7EXAMPLE" ]; then
    echo -e "${RED}❌ Using example Access Key ID (not real credentials)${NC}"
else
    echo -e "${GREEN}✅ Not using example credentials${NC}"
fi

echo

# Summary
echo -e "${BLUE}📊 Summary${NC}"
echo -e "${BLUE}=========${NC}"

if [ $TEST1_EXIT -eq 0 ]; then
    echo -e "${GREEN}🎉 AWS connection is working!${NC}"
    echo
    echo -e "${BLUE}Your AWS account details:${NC}"
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    USER_ARN=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null)
    echo -e "   Account ID: $ACCOUNT_ID"
    echo -e "   User ARN: $USER_ARN"
else
    echo -e "${RED}❌ AWS connection is not working${NC}"
    echo
    echo -e "${YELLOW}💡 Troubleshooting steps:${NC}"
    echo -e "${YELLOW}1. Check if your credentials are correct${NC}"
    echo -e "${YELLOW}2. If using Vocareum, credentials may be expired${NC}"
    echo -e "${YELLOW}3. Ensure you have internet connectivity${NC}"
    echo -e "${YELLOW}4. Try refreshing your credentials${NC}"
    echo
    echo -e "${YELLOW}🔄 To update credentials:${NC}"
    echo -e "${YELLOW}   ./setup-environment.sh interactive${NC}"
fi

echo
