#!/bin/bash

# NVIDIA NIM Model Deployment Script for Lumina
# Automates the EKS cluster setup and NIM deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME=${CLUSTER_NAME:-"lumina-nim-cluster"}
CLUSTER_NODE_TYPE=${CLUSTER_NODE_TYPE:-"g6e.xlarge"}
NODE_COUNT=${NODE_COUNT:-1}
NAMESPACE=${NAMESPACE:-"nim"}
NIM_MODEL=${NIM_MODEL:-"nvcr.io/nim/nvidia/llama-3.1-nemotron-nano-8b-v1"}

echo -e "${BLUE}🚀 Starting NVIDIA NIM Deployment for Lumina${NC}"
echo -e "${YELLOW}Cluster: $CLUSTER_NAME${NC}"
echo -e "${YELLOW}Node Type: $CLUSTER_NODE_TYPE${NC}"
echo -e "${YELLOW}Model: $NIM_MODEL${NC}"

# Load environment configuration
load_environment() {
    if [ -f ".env" ]; then
        echo -e "${BLUE}📋 Loading environment configuration...${NC}"
        export $(grep -v '^#' .env | xargs)
    else
        echo -e "${YELLOW}⚠️  .env file not found, using environment variables${NC}"
    fi
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}📋 Checking prerequisites...${NC}"
    
    # Load environment first
    load_environment
    
    # Check if NGC_CLI_API_KEY is set
    if [ -z "$NGC_CLI_API_KEY" ]; then
        echo -e "${RED}❌ NGC_CLI_API_KEY not found${NC}"
        echo -e "${YELLOW}Please run: ./setup-environment.sh${NC}"
        exit 1
    fi
    
    # Check AWS credentials
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        echo -e "${RED}❌ AWS credentials not found${NC}"
        echo -e "${YELLOW}Please run: ./setup-environment.sh${NC}"
        exit 1
    fi
    
    # Check if eksctl is available
    if ! command -v eksctl &> /dev/null; then
        echo -e "${RED}❌ eksctl is not installed${NC}"
        echo -e "${YELLOW}Installing eksctl...${NC}"
        curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
        sudo mv /tmp/eksctl /usr/local/bin
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed${NC}"
        echo -e "${YELLOW}Installing kubectl...${NC}"
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        sudo mv kubectl /usr/local/bin/
    fi
    
    # Check if helm is available
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}❌ helm is not installed${NC}"
        echo -e "${YELLOW}Installing helm...${NC}"
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi
    
    echo -e "${GREEN}✅ Prerequisites check completed${NC}"
}

# Create EKS cluster
create_cluster() {
    echo -e "${BLUE}🏗️  Creating EKS cluster...${NC}"
    
    # Check if cluster already exists
    if eksctl get cluster --name=$CLUSTER_NAME &> /dev/null; then
        echo -e "${YELLOW}⚠️  Cluster $CLUSTER_NAME already exists${NC}"
        read -p "Do you want to use the existing cluster? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}❌ Deployment cancelled${NC}"
            exit 1
        fi
    else
        eksctl create cluster \
            --name=$CLUSTER_NAME \
            --node-type=$CLUSTER_NODE_TYPE \
            --nodes=$NODE_COUNT \
            --region=$AWS_DEFAULT_REGION
    fi
    
    # Verify cluster
    kubectl get nodes -o wide
    echo -e "${GREEN}✅ EKS cluster is ready${NC}"
}

# Setup storage
setup_storage() {
    echo -e "${BLUE}💾 Setting up EBS CSI driver...${NC}"
    
    # Associate OIDC provider
    eksctl utils associate-iam-oidc-provider --cluster $CLUSTER_NAME --approve
    
    # Create IAM service account for EBS CSI
    eksctl create iamserviceaccount \
        --name ebs-csi-controller-sa \
        --namespace kube-system \
        --cluster $CLUSTER_NAME \
        --role-name AmazonEKS_EBS_CSI_DriverRole \
        --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
        --approve || echo "Service account may already exist"
    
    # Create EBS CSI addon
    eksctl create addon \
        --name "aws-ebs-csi-driver" \
        --cluster $CLUSTER_NAME \
        --region=$AWS_DEFAULT_REGION \
        --service-account-role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/AmazonEKS_EBS_CSI_DriverRole \
        --force || echo "Addon may already exist"
    
    # Wait for addon to be ready
    echo -e "${YELLOW}⏳ Waiting for EBS CSI driver to be ready...${NC}"
    while true; do
        STATUS=$(eksctl get addon --name "aws-ebs-csi-driver" --region $AWS_DEFAULT_REGION --cluster $CLUSTER_NAME -o json | jq -r '.[0].Status')
        if [ "$STATUS" = "ACTIVE" ]; then
            break
        fi
        echo "Current status: $STATUS"
        sleep 10
    done
    
    # Create storage class
    cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
    name: ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
EOF
    
    echo -e "${GREEN}✅ Storage setup completed${NC}"
}

# Setup NIM namespace and secrets
setup_nim_namespace() {
    echo -e "${BLUE}🔐 Setting up NIM namespace and secrets...${NC}"
    
    # Create namespace
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Create docker registry secret
    kubectl create secret docker-registry registry-secret \
        --docker-server=nvcr.io \
        --docker-username='$oauthtoken' \
        --docker-password=$NGC_CLI_API_KEY \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create NGC API secret
    kubectl create secret generic ngc-api \
        --from-literal=NGC_API_KEY=$NGC_CLI_API_KEY \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
    
    echo -e "${GREEN}✅ Namespace and secrets created${NC}"
}

# Download and deploy NIM
deploy_nim() {
    echo -e "${BLUE}🤖 Deploying NVIDIA NIM...${NC}"
    
    # Download NIM Helm chart
    if [ ! -f "nim-llm-1.7.0.tgz" ]; then
        helm fetch https://helm.ngc.nvidia.com/nim/charts/nim-llm-1.7.0.tgz \
            --username='$oauthtoken' \
            --password=$NGC_CLI_API_KEY
    fi
    
    # Create custom values file
    cat <<EOF > nim_custom_values.yaml
image:
  repository: "$NIM_MODEL"
  tag: latest
model:
  ngcAPISecret: ngc-api
  modelName: "llama-3.1-nemotron-nano-8b-v1"
env:
  - name: NIM_ENABLE_AUTO_TOOL_CHOICE
    value: "1"
  - name: NIM_TOOL_CALL_PARSER
    value: "llama_nemotron_json"
persistence:
  enabled: true
  storageClass: "ebs-sc"
  accessMode: ReadWriteOnce
  stsPersistentVolumeClaimRetentionPolicy:
      whenDeleted: Retain
      whenScaled: Retain
imagePullSecrets:
  - name: registry-secret
resources:
  limits:
    nvidia.com/gpu: 1
  requests:
    nvidia.com/gpu: 1
EOF
    
    # Install NIM
    helm upgrade --install lumina-nim nim-llm-1.7.0.tgz \
        -f nim_custom_values.yaml \
        --namespace $NAMESPACE \
        --wait \
        --timeout=20m
    
    echo -e "${GREEN}✅ NIM deployment completed${NC}"
}

# Setup public access
setup_public_access() {
    echo -e "${BLUE}🌐 Setting up public access...${NC}"
    
    # Get service labels
    INSTANCE_LABEL=$(kubectl get svc lumina-nim-nim-llm -n $NAMESPACE -o jsonpath='{.metadata.labels.app\.kubernetes\.io/instance}')
    NAME_LABEL=$(kubectl get svc lumina-nim-nim-llm -n $NAMESPACE -o jsonpath='{.metadata.labels.app\.kubernetes\.io/name}')
    
    # Create public service
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: nim-public
  namespace: $NAMESPACE
spec:
  selector:
    app.kubernetes.io/name: $NAME_LABEL
    app.kubernetes.io/instance: $INSTANCE_LABEL
  ports:
    - name: http
      port: 8000
      targetPort: 8000
      protocol: TCP
  type: LoadBalancer
EOF
    
    # Wait for external IP
    echo -e "${YELLOW}⏳ Waiting for LoadBalancer external IP...${NC}"
    while true; do
        EXTERNAL_IP=$(kubectl get svc nim-public -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        if [ ! -z "$EXTERNAL_IP" ] && [ "$EXTERNAL_IP" != "null" ]; then
            break
        fi
        echo "Waiting for external IP..."
        sleep 10
    done
    
    echo -e "${GREEN}✅ Public access configured${NC}"
    echo -e "${BLUE}🔗 NIM API Endpoint: http://$EXTERNAL_IP:8000${NC}"
    
    # Save endpoint to file
    echo "NIM_ENDPOINT_URL=http://$EXTERNAL_IP:8000" > nim-endpoint.env
    echo -e "${YELLOW}📝 Endpoint saved to nim-endpoint.env${NC}"
}

# Test deployment
test_deployment() {
    echo -e "${BLUE}🧪 Testing NIM deployment...${NC}"
    
    source nim-endpoint.env
    
    # Test models endpoint
    echo -e "${YELLOW}Testing /v1/models endpoint...${NC}"
    curl -s "$NIM_ENDPOINT_URL/v1/models" | jq '.' || echo "Models endpoint test failed"
    
    # Test chat completion
    echo -e "${YELLOW}Testing chat completion...${NC}"
    curl -s -X POST "$NIM_ENDPOINT_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
            "messages": [
                {"role": "user", "content": "Hello from Lumina!"}
            ],
            "max_tokens": 50
        }' | jq '.choices[0].message.content' || echo "Chat completion test failed"
    
    echo -e "${GREEN}✅ Deployment test completed${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🎯 NVIDIA NIM Deployment for Lumina${NC}"
    echo -e "${BLUE}=====================================${NC}"
    
    check_prerequisites
    create_cluster
    setup_storage
    setup_nim_namespace
    deploy_nim
    setup_public_access
    test_deployment
    
    echo -e "${GREEN}🎉 NIM deployment completed successfully!${NC}"
    echo -e "${BLUE}📋 Summary:${NC}"
    echo -e "   Cluster: $CLUSTER_NAME"
    echo -e "   Namespace: $NAMESPACE"
    echo -e "   Model: $NIM_MODEL"
    echo -e "   Endpoint: $(cat nim-endpoint.env)"
    echo -e "${YELLOW}💡 Use 'source nim-endpoint.env' to load the endpoint URL${NC}"
}

# Handle script arguments
case "${1:-}" in
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up resources...${NC}"
        helm uninstall lumina-nim -n $NAMESPACE || true
        kubectl delete namespace $NAMESPACE || true
        eksctl delete cluster --name=$CLUSTER_NAME
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
    "test")
        if [ -f "nim-endpoint.env" ]; then
            test_deployment
        else
            echo -e "${RED}❌ nim-endpoint.env not found. Deploy first.${NC}"
        fi
        ;;
    *)
        main
        ;;
esac