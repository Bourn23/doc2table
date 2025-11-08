#!/bin/bash

# Lumina Environment Setup Script
# Configures AWS credentials and environment variables for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔧 Lumina Environment Setup${NC}"
echo -e "${PURPLE}===========================${NC}"

# Check if .env file exists
setup_env_file() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env file with your actual credentials${NC}"
        return 1
    else
        echo -e "${GREEN}✅ .env file already exists${NC}"
        return 0
    fi
}

# Load environment variables
load_env() {
    if [ -f ".env" ]; then
        echo -e "${BLUE}📋 Loading environment variables...${NC}"
        export $(grep -v '^#' .env | xargs)
        echo -e "${GREEN}✅ Environment variables loaded${NC}"
    else
        echo -e "${RED}❌ .env file not found${NC}"
        exit 1
    fi
}

# Configure AWS CLI
configure_aws() {
    echo -e "${BLUE}🔑 Configuring AWS CLI...${NC}"
    
    # Check if AWS credentials are set in environment
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        echo -e "${RED}❌ AWS credentials not found in .env file${NC}"
        echo -e "${YELLOW}Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN in .env${NC}"
        exit 1
    fi
    
    # Configure AWS CLI with credentials
    aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
    aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
    aws configure set default.region "$AWS_DEFAULT_REGION"
    
    # Set session token if provided (for Vocareum lab)
    if [ ! -z "$AWS_SESSION_TOKEN" ]; then
        aws configure set aws_session_token "$AWS_SESSION_TOKEN"
        echo -e "${GREEN}✅ AWS session token configured${NC}"
    fi
    
    # Test AWS connection
    echo -e "${YELLOW}🧪 Testing AWS connection...${NC}"
    if aws sts get-caller-identity > /dev/null 2>&1; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
        echo -e "${GREEN}✅ AWS connection successful${NC}"
        echo -e "${BLUE}   Account ID: $ACCOUNT_ID${NC}"
        echo -e "${BLUE}   User: $USER_ARN${NC}"
    else
        echo -e "${RED}❌ AWS connection failed${NC}"
        echo -e "${YELLOW}Please check your AWS credentials in .env file${NC}"
        exit 1
    fi
}

# Check Vocareum resource limits
check_vocareum_limits() {
    echo -e "${BLUE}📊 Checking Vocareum resource limits...${NC}"
    
    # Check current EC2 instances
    CURRENT_INSTANCES=$(aws ec2 describe-instances --query 'Reservations[*].Instances[?State.Name==`running`]' --output json | jq length)
    echo -e "${YELLOW}   Current EC2 instances: $CURRENT_INSTANCES/${MAX_EC2_INSTANCES:-2}${NC}"
    
    if [ "$CURRENT_INSTANCES" -ge "${MAX_EC2_INSTANCES:-2}" ]; then
        echo -e "${RED}⚠️  Warning: At EC2 instance limit${NC}"
    fi
    
    # Check current EKS clusters
    CURRENT_CLUSTERS=$(aws eks list-clusters --query 'clusters' --output json | jq length)
    echo -e "${YELLOW}   Current EKS clusters: $CURRENT_CLUSTERS/${MAX_EKS_CLUSTERS:-1}${NC}"
    
    if [ "$CURRENT_CLUSTERS" -ge "${MAX_EKS_CLUSTERS:-1}" ]; then
        echo -e "${RED}⚠️  Warning: At EKS cluster limit${NC}"
    fi
    
    echo -e "${GREEN}✅ Resource limit check completed${NC}"
}

# Validate required tools
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    local missing_tools=()
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}⚠️  kubectl not found, will install during deployment${NC}"
    fi
    
    # Check eksctl
    if ! command -v eksctl &> /dev/null; then
        echo -e "${YELLOW}⚠️  eksctl not found, will install during deployment${NC}"
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        echo -e "${YELLOW}⚠️  helm not found, will install during deployment${NC}"
    fi
    
    # Check jq
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing required tools: ${missing_tools[*]}${NC}"
        echo -e "${YELLOW}Please install the missing tools before proceeding${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check completed${NC}"
}

# Create AWS credentials file for compatibility
create_aws_credentials() {
    echo -e "${BLUE}📁 Creating AWS credentials file...${NC}"
    
    mkdir -p ~/.aws
    
    cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
EOF
    
    if [ ! -z "$AWS_SESSION_TOKEN" ]; then
        echo "aws_session_token = $AWS_SESSION_TOKEN" >> ~/.aws/credentials
    fi
    
    cat > ~/.aws/config << EOF
[default]
region = $AWS_DEFAULT_REGION
output = json
EOF
    
    echo -e "${GREEN}✅ AWS credentials file created${NC}"
}

# Validate NGC API key
validate_ngc_key() {
    echo -e "${BLUE}🔑 Validating NGC API key...${NC}"
    
    if [ -z "$NGC_CLI_API_KEY" ]; then
        echo -e "${RED}❌ NGC_CLI_API_KEY not found in .env file${NC}"
        echo -e "${YELLOW}Please get your API key from: https://catalog.ngc.nvidia.com/${NC}"
        exit 1
    fi
    
    # Test NGC API key by trying to access a public model
    if curl -s -H "Authorization: Bearer $NGC_CLI_API_KEY" \
        "https://api.ngc.nvidia.com/v2/models" > /dev/null; then
        echo -e "${GREEN}✅ NGC API key is valid${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not validate NGC API key (network issue or invalid key)${NC}"
        echo -e "${YELLOW}Proceeding anyway - will be validated during NIM deployment${NC}"
    fi
}

# Generate deployment summary
generate_setup_summary() {
    echo -e "${PURPLE}📋 Setup Summary${NC}"
    echo -e "${PURPLE}===============${NC}"
    
    echo -e "${BLUE}🔧 Configuration:${NC}"
    echo -e "   AWS Region: $AWS_DEFAULT_REGION"
    echo -e "   Cluster Name: $CLUSTER_NAME"
    echo -e "   Node Type: $CLUSTER_NODE_TYPE"
    echo -e "   Instance Type: $INSTANCE_TYPE"
    
    echo -e "${BLUE}🎯 Ready for Deployment:${NC}"
    echo -e "   ./deploy-lumina.sh        - Deploy complete stack"
    echo -e "   ./deploy-model.sh         - Deploy NIM models only"
    echo -e "   ./deploy-backend.sh       - Deploy backend only"
    
    echo -e "${BLUE}💰 Estimated Costs:${NC}"
    echo -e "   EKS Cluster: ~$36/day"
    echo -e "   EC2 Backend: ~$36/day"
    echo -e "   Storage & Transfer: ~$5/day"
    echo -e "   Total: ~$77/day"
    
    # Save setup info
    cat > setup-info.json << EOF
{
    "setup_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "aws_region": "$AWS_DEFAULT_REGION",
    "aws_account": "$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 'unknown')",
    "cluster_name": "$CLUSTER_NAME",
    "node_type": "$CLUSTER_NODE_TYPE",
    "instance_type": "$INSTANCE_TYPE",
    "estimated_daily_cost": 77
}
EOF
    
    echo -e "${YELLOW}💾 Setup info saved to setup-info.json${NC}"
}

# Interactive setup mode
interactive_setup() {
    echo -e "${BLUE}🎯 Interactive Setup Mode${NC}"
    echo -e "${BLUE}========================${NC}"
    
    # NGC API Key
    if [ -z "$NGC_CLI_API_KEY" ]; then
        echo -e "${YELLOW}Please enter your NVIDIA NGC API Key:${NC}"
        read -p "NGC API Key: " ngc_key
        sed -i.bak "s/NGC_CLI_API_KEY=.*/NGC_CLI_API_KEY=$ngc_key/" .env
    fi
    
    # AWS Credentials
    if [ -z "$AWS_ACCESS_KEY_ID" ]; then
        echo -e "${YELLOW}Please enter your AWS credentials from Vocareum lab:${NC}"
        read -p "AWS Access Key ID: " aws_key_id
        read -p "AWS Secret Access Key: " aws_secret_key
        read -p "AWS Session Token: " aws_session_token
        read -p "AWS Region [us-east-1]: " aws_region
        aws_region=${aws_region:-us-east-1}
        
        sed -i.bak "s/AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$aws_key_id/" .env
        sed -i.bak "s/AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$aws_secret_key/" .env
        sed -i.bak "s/AWS_SESSION_TOKEN=.*/AWS_SESSION_TOKEN=$aws_session_token/" .env
        sed -i.bak "s/AWS_DEFAULT_REGION=.*/AWS_DEFAULT_REGION=$aws_region/" .env
    fi
    
    echo -e "${GREEN}✅ Interactive setup completed${NC}"
}

# Main execution
main() {
    case "${1:-}" in
        "interactive")
            setup_env_file || interactive_setup
            load_env
            configure_aws
            create_aws_credentials
            validate_ngc_key
            check_prerequisites
            check_vocareum_limits
            generate_setup_summary
            ;;
        "validate")
            load_env
            configure_aws
            validate_ngc_key
            check_vocareum_limits
            ;;
        *)
            if setup_env_file; then
                load_env
                configure_aws
                create_aws_credentials
                validate_ngc_key
                check_prerequisites
                check_vocareum_limits
                generate_setup_summary
            else
                echo -e "${YELLOW}Run './setup-environment.sh interactive' to configure credentials${NC}"
            fi
            ;;
    esac
}

main "$@"