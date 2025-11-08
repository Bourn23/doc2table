#!/bin/bash

# Deploy backend to personal AWS account (non-Vocareum)
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Backend to Personal AWS Account${NC}"
echo
echo -e "${YELLOW}⚠️  This will use YOUR AWS credentials and create resources in YOUR account${NC}"
echo -e "${YELLOW}💰 Estimated cost: ~\$30/month for t3.medium instance${NC}"
echo
echo -e "${BLUE}Prerequisites:${NC}"
echo -e "   • AWS CLI configured with your credentials (run: aws configure)"
echo -e "   • Or AWS credentials set via environment variables (run: ./setup-environment.sh and once done adding to .env, re-run it; then come back here)"
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo

# Prompt for configuration
read -p "Enter AWS region (default: us-east-1): " REGION
REGION=${REGION:-us-east-1}

read -p "Enter key pair name (default: lumina-backend-key): " KEY_NAME
KEY_NAME=${KEY_NAME:-lumina-backend-key}

read -p "Enter security group name (default: lumina-backend-sg): " SECURITY_GROUP
SECURITY_GROUP=${SECURITY_GROUP:-lumina-backend-sg}

read -p "Enter instance type (default: t3.medium): " INSTANCE_TYPE
INSTANCE_TYPE=${INSTANCE_TYPE:-t3.medium}

echo
echo -e "${YELLOW}📋 Configuration:${NC}"
echo -e "   Region: $REGION"
echo -e "   Key Name: $KEY_NAME"
echo -e "   Security Group: $SECURITY_GROUP"
echo -e "   Instance Type: $INSTANCE_TYPE"
echo
read -p "Continue with these settings? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured or credentials invalid${NC}"
    echo -e "${YELLOW}Please run: aws configure${NC}"
    echo -e "${YELLOW}Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials verified${NC}"

# Check if key pair exists, create if not
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME > /dev/null 2>&1; then
    echo -e "${YELLOW}🔑 Creating key pair: $KEY_NAME${NC}"
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 600 ${KEY_NAME}.pem
    echo -e "${GREEN}✅ Key pair created and saved as ${KEY_NAME}.pem${NC}"
else
    echo -e "${GREEN}✅ Key pair $KEY_NAME already exists${NC}"
    if [ ! -f "${KEY_NAME}.pem" ]; then
        echo -e "${RED}❌ Key file ${KEY_NAME}.pem not found locally${NC}"
        echo -e "${YELLOW}💡 Please download your key pair from AWS Console or use an existing one${NC}"
        exit 1
    fi
fi

# Check if security group exists, create if not
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP > /dev/null 2>&1; then
    echo -e "${YELLOW}🔒 Creating security group: $SECURITY_GROUP${NC}"
    
    # Get default VPC ID
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)
    
    # Create security group
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "Lumina Backend Security Group" \
        --vpc-id $VPC_ID \
        --query 'GroupId' --output text)
    
    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8001 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8002 \
        --cidr 0.0.0.0/0
    
    echo -e "${GREEN}✅ Security group created with ID: $SECURITY_GROUP_ID${NC}"
else
    echo -e "${GREEN}✅ Security group $SECURITY_GROUP already exists${NC}"
fi

# Create user data script for EC2 initialization
cat > user-data-personal.sh << 'EOF'
#!/bin/bash
yum update -y

# Install modern Docker
amazon-linux-extras install docker -y

# Manually install the Docker Compose V2 Plugin
COMPOSE_URL="https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)"
curl -SL $COMPOSE_URL -o /usr/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/libexec/docker/cli-plugins/docker-compose

# Manually install/upgrade Docker Buildx
# The t3.medium is x86_64, which is amd64
BUILDX_URL="https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64"
curl -SL $BUILDX_URL -o /usr/libexec/docker/cli-plugins/docker-buildx
chmod +x /usr/libexec/docker/cli-plugins/docker-buildx

# Start services
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Git
yum install -y git

# Create application directory
mkdir -p /home/ec2-user/lumina
chown ec2-user:ec2-user /home/ec2-user/lumina

echo "User data script completed at $(date)" >> /var/log/user-data.log
EOF

# Launch EC2 instance
echo -e "${BLUE}🚀 Launching EC2 instance...${NC}"

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-groups $SECURITY_GROUP \
    --user-data file://user-data-personal.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lumina-backend},{Key=Project,Value=lumina}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo -e "${YELLOW}Instance ID: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo -e "${GREEN}✅ Instance is running at: $PUBLIC_IP${NC}"

# Save instance info
cat > backend-instance-personal.env << EOF
INSTANCE_ID=$INSTANCE_ID
PUBLIC_IP=$PUBLIC_IP
KEY_NAME=$KEY_NAME
BACKEND_ENDPOINT_URL=http://$PUBLIC_IP:8000
REGION=$REGION
EOF

echo -e "${BLUE}📦 Waiting for instance initialization...${NC}"
sleep 60

# Test SSH connection
echo -e "${YELLOW}🔑 Testing SSH connection...${NC}"
if ssh -i ${KEY_NAME}.pem -o ConnectTimeout=10 -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP "echo 'SSH Ready'"; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo -e "${YELLOW}💡 Instance may still be initializing. Try again in a few minutes.${NC}"
    echo -e "${YELLOW}💡 Command to connect: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP${NC}"
    exit 1
fi

# Clean up temporary files
rm -f user-data-personal.sh

echo -e "${GREEN}🎉 Backend instance deployed successfully!${NC}"
echo -e "${BLUE}📋 Connection details:${NC}"
echo -e "   Instance ID: $INSTANCE_ID"
echo -e "   Public IP: $PUBLIC_IP"
echo -e "   SSH: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo -e "   Backend URL: http://$PUBLIC_IP:8000"
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "   1. Run: ./deploy-to-existing-backend-personal.sh"
echo -e "   2. Or manually copy your application code to the instance"
echo -e "${YELLOW}💰 Cost: ~$0.05/hour for t3.medium instance${NC}"