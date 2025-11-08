#!/bin/bash

# Lumina Setup Validation Script
# Tests all prerequisites and configurations before deployment

# Note: Not using set -e to allow tests to continue even if some fail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Lumina Setup Validation${NC}"
echo -e "${BLUE}==========================${NC}"

# Load environment
if [ -f ".env" ]; then
    set -a  # automatically export all variables
    source .env
    set +a  # turn off automatic export
else
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}Run: cp .env.example .env and configure it${NC}"
    exit 1
fi

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command" &> /dev/null; then
        echo -e "${GREEN}✅ $test_name - PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ $test_name - FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Environment variable tests
echo -e "${BLUE}📋 Environment Variables${NC}"
run_test "NGC API Key set" "[ ! -z '$NGC_CLI_API_KEY' ]"
run_test "AWS Access Key set" "[ ! -z '$AWS_ACCESS_KEY_ID' ]"
run_test "AWS Secret Key set" "[ ! -z '$AWS_SECRET_ACCESS_KEY' ]"
run_test "AWS Session Token set" "[ ! -z '$AWS_SESSION_TOKEN' ]"
run_test "AWS Region set" "[ ! -z '$AWS_DEFAULT_REGION' ]"

# Tool availability tests
echo -e "${BLUE}🔧 Required Tools${NC}"
run_test "AWS CLI available" "command -v aws"
run_test "Docker available" "command -v docker"
run_test "jq available" "command -v jq"
run_test "curl available" "command -v curl"

# AWS connectivity tests
echo -e "${BLUE}☁️  AWS Connectivity${NC}"
run_test "AWS credentials valid" "aws sts get-caller-identity"
run_test "EC2 access" "aws ec2 describe-regions --region $AWS_DEFAULT_REGION"
run_test "EKS access" "aws eks list-clusters --region $AWS_DEFAULT_REGION"
run_test "S3 access" "aws s3 ls"

# NGC connectivity tests
echo -e "${BLUE}🤖 NVIDIA NGC${NC}"
run_test "NGC API reachable" "curl -s --max-time 10 https://api.ngc.nvidia.com/v2/models"

# Resource limit checks
echo -e "${BLUE}📊 Resource Limits${NC}"
CURRENT_INSTANCES=$(aws ec2 describe-instances --query 'Reservations[*].Instances[?State.Name==`running`]' --output json | jq length 2>/dev/null || echo "0")
CURRENT_CLUSTERS=$(aws eks list-clusters --query 'clusters' --output json | jq length 2>/dev/null || echo "0")

echo -e "${YELLOW}Current EC2 instances: $CURRENT_INSTANCES/2${NC}"
echo -e "${YELLOW}Current EKS clusters: $CURRENT_CLUSTERS/1${NC}"

if [ "$CURRENT_INSTANCES" -lt 2 ]; then
    echo -e "${GREEN}✅ EC2 capacity available${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ EC2 at capacity limit${NC}"
    ((TESTS_FAILED++))
fi

if [ "$CURRENT_CLUSTERS" -lt 1 ]; then
    echo -e "${GREEN}✅ EKS capacity available${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ EKS at capacity limit${NC}"
    ((TESTS_FAILED++))
fi

# File permissions
echo -e "${BLUE}📁 File Permissions${NC}"
run_test "deploy-lumina.sh executable" "[ -x deploy-lumina.sh ]"
run_test "deploy-model.sh executable" "[ -x deploy-model.sh ]"
run_test "deploy-backend.sh executable" "[ -x deploy-backend.sh ]"
run_test "setup-environment.sh executable" "[ -x setup-environment.sh ]"

# Summary
echo -e "${BLUE}📊 Validation Summary${NC}"
echo -e "${BLUE}===================${NC}"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Ready for deployment.${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "   ./deploy-lumina.sh        - Deploy complete stack"
    echo -e "   ./deploy-model.sh         - Deploy NIM models only"
    echo -e "   ./deploy-backend.sh       - Deploy backend only"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please fix the issues before deployment.${NC}"
    echo -e "${YELLOW}Common fixes:${NC}"
    echo -e "   - Run: ./setup-environment.sh interactive"
    echo -e "   - Check Vocareum credentials are fresh"
    echo -e "   - Verify NGC API key is correct"
    echo -e "   - Install missing tools (aws-cli, docker, jq)"
    exit 1
fi