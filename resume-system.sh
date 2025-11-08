#!/bin/bash

# Lumina System Resume Script
# Resumes/restarts AWS resources after pause

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}▶️  Resuming Lumina System${NC}"
echo -e "${PURPLE}==========================${NC}"

# Load environment
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Load pause state
if [ ! -f "pause-state.env" ]; then
    echo -e "${RED}❌ pause-state.env not found${NC}"
    echo -e "${YELLOW}Cannot resume without pause state file${NC}"
    echo -e "${YELLOW}If you need to start fresh, run: ./deploy-lumina.sh${NC}"
    exit 1
fi

# Load pause state
set -a
source pause-state.env
set +a

echo -e "${BLUE}📋 Loading pause state from: $(date -d "$PAUSE_TIMESTAMP" 2>/dev/null || echo "$PAUSE_TIMESTAMP")${NC}"

# Initialize counters
RESOURCES_RESUMED=0
RESOURCES_FAILED=0

# Function to resume a resource
resume_resource() {
    local resource_name="$1"
    local resume_command="$2"
    
    echo -e "${YELLOW}▶️  Resuming: $resource_name${NC}"
    
    if eval "$resume_command" &> /dev/null; then
        echo -e "${GREEN}✅ $resource_name resumed successfully${NC}"
        ((RESOURCES_RESUMED++))
    else
        echo -e "${RED}❌ Failed to resume $resource_name${NC}"
        ((RESOURCES_FAILED++))
    fi
}

# Resume EC2 instances
resume_ec2_instances() {
    echo -e "${BLUE}🔄 Resuming EC2 Instances...${NC}"
    
    if [ ! -z "$EC2_INSTANCE_IDS" ]; then
        for instance_id in $EC2_INSTANCE_IDS; do
            echo -e "${YELLOW}▶️  Starting instance: $instance_id${NC}"
            
            # Check current state
            CURRENT_STATE=$(aws ec2 describe-instances \
                --instance-ids "$instance_id" \
                --query 'Reservations[0].Instances[0].State.Name' \
                --output text 2>/dev/null || echo "not-found")
            
            if [ "$CURRENT_STATE" = "stopped" ]; then
                aws ec2 start-instances --instance-ids "$instance_id" &> /dev/null && \
                    echo -e "${GREEN}✅ Instance $instance_id starting${NC}" || \
                    echo -e "${RED}❌ Failed to start $instance_id${NC}"
                
                # Wait for instance to be running
                echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
                aws ec2 wait instance-running --instance-ids "$instance_id" && \
                    echo -e "${GREEN}✅ Instance $instance_id is running${NC}"
                
            elif [ "$CURRENT_STATE" = "running" ]; then
                echo -e "${GREEN}✅ Instance $instance_id already running${NC}"
            else
                echo -e "${YELLOW}⚠️  Instance $instance_id state: $CURRENT_STATE${NC}"
            fi
        done
        ((RESOURCES_RESUMED++))
    else
        echo -e "${YELLOW}⚠️  No EC2 instances to resume${NC}"
    fi
}

# Resume EKS cluster
resume_eks_cluster() {
    echo -e "${BLUE}🔄 Resuming EKS Cluster...${NC}"
    
    if aws eks describe-cluster --name "$CLUSTER_NAME" &> /dev/null; then
        # Get node groups
        NODE_GROUPS=$(aws eks list-nodegroups --cluster-name "$CLUSTER_NAME" --query 'nodegroups' --output text)
        
        if [ ! -z "$NODE_GROUPS" ] && [ "$NODE_GROUPS" != "None" ]; then
            for nodegroup in $NODE_GROUPS; do
                # Get saved capacity
                CAPACITY_VAR="EKS_NODEGROUP_${nodegroup}_CAPACITY"
                DESIRED_CAPACITY=${!CAPACITY_VAR:-1}
                
                echo -e "${YELLOW}▶️  Scaling up node group: $nodegroup to $DESIRED_CAPACITY nodes${NC}"
                
                aws eks update-nodegroup-config \
                    --cluster-name "$CLUSTER_NAME" \
                    --nodegroup-name "$nodegroup" \
                    --scaling-config desiredSize=$DESIRED_CAPACITY,minSize=0,maxSize=2 &> /dev/null && \
                    echo -e "${GREEN}✅ Node group $nodegroup scaling up${NC}" || \
                    echo -e "${RED}❌ Failed to scale up $nodegroup${NC}"
            done
            
            # Wait for nodes to be ready
            echo -e "${YELLOW}⏳ Waiting for EKS nodes to be ready...${NC}"
            sleep 30
            
            # Check node status
            kubectl get nodes &> /dev/null && \
                echo -e "${GREEN}✅ EKS nodes are ready${NC}" || \
                echo -e "${YELLOW}⚠️  EKS nodes still starting up${NC}"
            
            ((RESOURCES_RESUMED++))
        else
            echo -e "${YELLOW}⚠️  No node groups found${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  EKS cluster $CLUSTER_NAME not found${NC}"
    fi
}

# Resume RDS instances
resume_rds_instances() {
    echo -e "${BLUE}🔄 Resuming RDS Instances...${NC}"
    
    if [ ! -z "$RDS_INSTANCE_IDS" ]; then
        for db_instance in $RDS_INSTANCE_IDS; do
            echo -e "${YELLOW}▶️  Starting RDS instance: $db_instance${NC}"
            
            # Check current state
            CURRENT_STATE=$(aws rds describe-db-instances \
                --db-instance-identifier "$db_instance" \
                --query 'DBInstances[0].DBInstanceStatus' \
                --output text 2>/dev/null || echo "not-found")
            
            if [ "$CURRENT_STATE" = "stopped" ]; then
                aws rds start-db-instance --db-instance-identifier "$db_instance" &> /dev/null && \
                    echo -e "${GREEN}✅ RDS instance $db_instance starting${NC}" || \
                    echo -e "${RED}❌ Failed to start $db_instance${NC}"
            elif [ "$CURRENT_STATE" = "available" ]; then
                echo -e "${GREEN}✅ RDS instance $db_instance already running${NC}"
            else
                echo -e "${YELLOW}⚠️  RDS instance $db_instance state: $CURRENT_STATE${NC}"
            fi
        done
        ((RESOURCES_RESUMED++))
    else
        echo -e "${YELLOW}⚠️  No RDS instances to resume${NC}"
    fi
}

# Wait for NIM pods to be ready
wait_for_nim_pods() {
    echo -e "${BLUE}🤖 Checking NIM pods...${NC}"
    
    if kubectl get namespace nim &> /dev/null; then
        echo -e "${YELLOW}⏳ Waiting for NIM pods to be ready...${NC}"
        
        # Wait up to 10 minutes for pods to be ready
        timeout=600
        elapsed=0
        
        while [ $elapsed -lt $timeout ]; do
            READY_PODS=$(kubectl get pods -n nim --no-headers 2>/dev/null | grep -c "Running" || echo "0")
            TOTAL_PODS=$(kubectl get pods -n nim --no-headers 2>/dev/null | wc -l || echo "0")
            
            if [ "$READY_PODS" -gt 0 ] && [ "$READY_PODS" -eq "$TOTAL_PODS" ]; then
                echo -e "${GREEN}✅ NIM pods are ready ($READY_PODS/$TOTAL_PODS)${NC}"
                break
            fi
            
            echo -e "${YELLOW}⏳ NIM pods status: $READY_PODS/$TOTAL_PODS ready${NC}"
            sleep 30
            elapsed=$((elapsed + 30))
        done
        
        if [ $elapsed -ge $timeout ]; then
            echo -e "${YELLOW}⚠️  Timeout waiting for NIM pods. Check manually with: kubectl get pods -n nim${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  NIM namespace not found${NC}"
    fi
}

# Update endpoints after resume
update_endpoints() {
    echo -e "${BLUE}🔗 Updating endpoints...${NC}"
    
    # Get new EC2 public IP if instances were resumed
    if [ ! -z "$EC2_INSTANCE_IDS" ]; then
        for instance_id in $EC2_INSTANCE_IDS; do
            NEW_PUBLIC_IP=$(aws ec2 describe-instances \
                --instance-ids "$instance_id" \
                --query 'Reservations[0].Instances[0].PublicIpAddress' \
                --output text 2>/dev/null || echo "")
            
            if [ ! -z "$NEW_PUBLIC_IP" ] && [ "$NEW_PUBLIC_IP" != "None" ]; then
                echo "PUBLIC_IP=$NEW_PUBLIC_IP" > backend-instance-resumed.env
                echo "BACKEND_ENDPOINT_URL=http://$NEW_PUBLIC_IP:8000" >> backend-instance-resumed.env
                echo -e "${GREEN}✅ New backend endpoint: http://$NEW_PUBLIC_IP:8000${NC}"
            fi
        done
    fi
    
    # Get new NIM LoadBalancer endpoint
    if kubectl get svc nim-public -n nim &> /dev/null; then
        echo -e "${YELLOW}⏳ Waiting for NIM LoadBalancer...${NC}"
        
        # Wait for external IP
        timeout=300
        elapsed=0
        
        while [ $elapsed -lt $timeout ]; do
            EXTERNAL_IP=$(kubectl get svc nim-public -n nim -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
            
            if [ ! -z "$EXTERNAL_IP" ] && [ "$EXTERNAL_IP" != "null" ]; then
                echo "NIM_ENDPOINT_URL=http://$EXTERNAL_IP:8000" > nim-endpoint-resumed.env
                echo -e "${GREEN}✅ New NIM endpoint: http://$EXTERNAL_IP:8000${NC}"
                break
            fi
            
            sleep 10
            elapsed=$((elapsed + 10))
        done
        
        if [ $elapsed -ge $timeout ]; then
            echo -e "${YELLOW}⚠️  Timeout waiting for NIM LoadBalancer. Check manually with: kubectl get svc -n nim${NC}"
        fi
    fi
}

# Test resumed services
test_resumed_services() {
    echo -e "${BLUE}🧪 Testing resumed services...${NC}"
    
    # Test NIM endpoint
    if [ -f "nim-endpoint-resumed.env" ]; then
        source nim-endpoint-resumed.env
        echo -e "${YELLOW}Testing NIM endpoint...${NC}"
        if curl -s --max-time 10 "$NIM_ENDPOINT_URL/v1/models" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ NIM endpoint is responding${NC}"
        else
            echo -e "${YELLOW}⚠️  NIM endpoint not ready yet (may need more time)${NC}"
        fi
    fi
    
    # Test backend endpoint
    if [ -f "backend-instance-resumed.env" ]; then
        source backend-instance-resumed.env
        echo -e "${YELLOW}Testing backend endpoint...${NC}"
        if curl -s --max-time 10 "$BACKEND_ENDPOINT_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend endpoint is responding${NC}"
        else
            echo -e "${YELLOW}⚠️  Backend endpoint not ready yet (may need more time)${NC}"
        fi
    fi
}

# Main resume execution
main() {
    echo -e "${BLUE}📋 Resume Plan:${NC}"
    
    # Show what will be resumed
    if [ ! -z "$EC2_INSTANCE_IDS" ]; then
        echo -e "   ▶️  EC2 instances: $(echo $EC2_INSTANCE_IDS | wc -w) instances"
    fi
    if grep -q "EKS_NODEGROUP" pause-state.env; then
        echo -e "   ▶️  EKS cluster nodes"
    fi
    if [ ! -z "$RDS_INSTANCE_IDS" ]; then
        echo -e "   ▶️  RDS instances: $RDS_INSTANCE_IDS"
    fi
    
    echo -e "${YELLOW}⏳ Starting resume process...${NC}"
    
    resume_ec2_instances
    resume_rds_instances
    resume_eks_cluster
    wait_for_nim_pods
    update_endpoints
    test_resumed_services
    
    echo -e "${PURPLE}📊 Resume Summary${NC}"
    echo -e "${PURPLE}=================${NC}"
    echo -e "${GREEN}Resources Resumed: $RESOURCES_RESUMED${NC}"
    echo -e "${RED}Failed Operations: $RESOURCES_FAILED${NC}"
    
    if [ -f "nim-endpoint-resumed.env" ] || [ -f "backend-instance-resumed.env" ]; then
        echo -e "${BLUE}🔗 New Endpoints:${NC}"
        
        if [ -f "nim-endpoint-resumed.env" ]; then
            source nim-endpoint-resumed.env
            echo -e "   NIM API: $NIM_ENDPOINT_URL"
        fi
        
        if [ -f "backend-instance-resumed.env" ]; then
            source backend-instance-resumed.env
            echo -e "   Backend API: $BACKEND_ENDPOINT_URL"
        fi
        
        echo -e "${YELLOW}💡 Update your frontend configuration with new endpoints${NC}"
    fi
    
    # Calculate time paused
    if [ ! -z "$PAUSE_TIMESTAMP" ]; then
        PAUSE_EPOCH=$(date -d "$PAUSE_TIMESTAMP" +%s 2>/dev/null || echo "0")
        CURRENT_EPOCH=$(date +%s)
        PAUSED_HOURS=$(echo "scale=1; ($CURRENT_EPOCH - $PAUSE_EPOCH) / 3600" | bc -l 2>/dev/null || echo "unknown")
        
        if [ ! -z "$HOURLY_SAVINGS" ] && [ "$PAUSED_HOURS" != "unknown" ]; then
            TOTAL_SAVINGS=$(echo "scale=2; $HOURLY_SAVINGS * $PAUSED_HOURS" | bc -l 2>/dev/null || echo "unknown")
            echo -e "${GREEN}💰 Estimated savings during pause: ~$${TOTAL_SAVINGS} (${PAUSED_HOURS}h)${NC}"
        fi
    fi
    
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo -e "   1. Wait 5-10 minutes for all services to fully start"
    echo -e "   2. Test endpoints manually if needed"
    echo -e "   3. Update frontend with new backend URL if changed"
    echo -e "   4. Run ./validate-setup.sh to verify everything is working"
}

# Handle different resume modes
case "${1:-}" in
    "quick")
        echo -e "${YELLOW}🚀 Quick resume (EC2 only)${NC}"
        resume_ec2_instances
        update_endpoints
        ;;
    "eks")
        echo -e "${YELLOW}🚀 EKS resume only${NC}"
        resume_eks_cluster
        wait_for_nim_pods
        update_endpoints
        ;;
    *)
        main
        ;;
esac

echo -e "${GREEN}▶️  System resume completed!${NC}"
echo -e "${YELLOW}⚠️  Allow 5-10 minutes for all services to be fully ready${NC}"