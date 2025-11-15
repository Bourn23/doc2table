#!/bin/bash

# Lumina Setup Validation Script
# Checks if all required credentials are properly configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Lumina Setup Validation${NC}"
echo -e "${BLUE}=========================${NC}"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}💡 Run: ./setup-environment.sh interactive${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env file exists${NC}"
echo

# Load environment variables
source .env

# Validation counters
ERRORS=0
WARNINGS=0

# Function to check if a variable is set and not a placeholder
check_credential() {
    local var_name=$1
    local var_value=$2
    local placeholder=$3
    local required=$4
    
    if [ -z "$var_value" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ $var_name: Not set${NC}"
            ((ERRORS++))
        else
            echo -e "${YELLOW}⚠️  $var_name: Not set (optional)${NC}"
            ((WARNINGS++))
        fi
    elif [ "$var_value" = "$placeholder" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ $var_name: Still using placeholder value${NC}"
            ((ERRORS++))
        else
            echo -e "${YELLOW}⚠️  $var_name: Using placeholder (optional)${NC}"
            ((WARNINGS++))
        fi
    else
        # Mask the value for security
        masked_value="${var_value:0:8}...${var_value: -4}"
        echo -e "${GREEN}✅ $var_name: Configured ($masked_value)${NC}"
    fi
}

echo -e "${BLUE}📋 Checking Required Credentials${NC}"
echo -e "${BLUE}================================${NC}"

# Check NVIDIA API Keys
check_credential "NVIDIA_API_KEY" "$NVIDIA_API_KEY" "nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" "true"
check_credential "NGC_CLI_API_KEY" "$NGC_CLI_API_KEY" "nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" "true"

# Check Google Gemini API Key
check_credential "GOOGLE_GEMINI_API_KEY" "$GOOGLE_GEMINI_API_KEY" "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" "true"

echo

echo -e "${BLUE}📋 Checking AWS Credentials${NC}"
echo -e "${BLUE}===========================${NC}"

# Check AWS credentials
check_credential "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID" "AKIAIOSFODNN7EXAMPLE" "true"
check_credential "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY" "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" "true"
check_credential "AWS_SESSION_TOKEN" "$AWS_SESSION_TOKEN" "" "false"

if [ -n "$AWS_DEFAULT_REGION" ]; then
    echo -e "${GREEN}✅ AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION${NC}"
else
    echo -e "${YELLOW}⚠️  AWS_DEFAULT_REGION: Not set (will use default)${NC}"
    ((WARNINGS++))
fi

echo

# Test AWS connection if credentials are set
if [ $ERRORS -eq 0 ]; then
    echo -e "${BLUE}🧪 Testing AWS Connection${NC}"
    echo -e "${BLUE}=========================${NC}"
    
    if command -v aws &> /dev/null; then
        if aws sts get-caller-identity > /dev/null 2>&1; then
            ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
            USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
            echo -e "${GREEN}✅ AWS connection successful${NC}"
            echo -e "${BLUE}   Account ID: $ACCOUNT_ID${NC}"
            echo -e "${BLUE}   User: $USER_ARN${NC}"
        else
            echo -e "${RED}❌ AWS connection failed${NC}"
            echo -e "${YELLOW}   Your credentials may be invalid or expired${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "${YELLOW}⚠️  AWS CLI not installed, skipping connection test${NC}"
        ((WARNINGS++))
    fi
    echo
fi

# Summary
echo -e "${BLUE}📊 Validation Summary${NC}"
echo -e "${BLUE}====================${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 Perfect! All credentials are properly configured${NC}"
    echo
    echo -e "${BLUE}✨ You're ready to deploy!${NC}"
    echo -e "${YELLOW}   Next steps:${NC}"
    echo -e "${YELLOW}   1. Run: ./manage-lumina.sh${NC}"
    echo -e "${YELLOW}   2. Select Option 2: Deploy Backend${NC}"
    echo -e "${YELLOW}   3. Select Option 3: Deploy Frontend${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All required credentials are configured${NC}"
    echo -e "${YELLOW}⚠️  $WARNINGS optional items not configured${NC}"
    echo
    echo -e "${BLUE}✨ You're ready to deploy!${NC}"
    echo -e "${YELLOW}   Next steps:${NC}"
    echo -e "${YELLOW}   1. Run: ./manage-lumina.sh${NC}"
    echo -e "${YELLOW}   2. Select Option 2: Deploy Backend${NC}"
    echo -e "${YELLOW}   3. Select Option 3: Deploy Frontend${NC}"
else
    echo -e "${RED}❌ $ERRORS required credentials missing or invalid${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS optional items not configured${NC}"
    fi
    echo
    echo -e "${YELLOW}💡 To fix this:${NC}"
    echo -e "${YELLOW}   Run: ./setup-environment.sh interactive${NC}"
    echo
    exit 1
fi

echo
echo -e "${BLUE}📝 Configuration File Locations${NC}"
echo -e "${BLUE}===============================${NC}"
echo -e "   Root config: .env (this file)"
echo -e "   Template: .env.example"
echo -e "   Backend config: Created automatically during deployment"
echo

exit 0
