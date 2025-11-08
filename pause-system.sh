#!/bin/bash

# Lumina System Pause Script
# Stops/pauses AWS resources to save costs during breaks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}⏸️  Pausing Lumina System${NC}"
echo -e "${PURPLE}=========================${NC}"

# Load environment
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Initialize counters
RESOURCES_PAUSED=0
RESOURCES_FAILED=0

# Function to pause a resource
pause_resource() {
    local resource_name="$1"
    local pause_command="$2"
    
    echo -e "${YELLOW}⏸️  Pausing: $resource_name${NC}"
    
    if eval "$pause_command" &> /dev/null; then
        echo -e "${GREEN}✅ $resource_name paused successfully${NC}"
        ((RESOURCES_PAUSED++))
    else
        echo -e "${RED}❌ Failed to pause $resource_name${NC}"
        ((RESOURCES_FAILED++))
    fi
}

# Create pause state file
create_pause_state() {
    echo -e "${BLUE}📝 Saving system state...${NC}"
    
    cat > pause-state.json << EOF
{
    "pause_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "paused_resources": [],
    "nim_endpoint": "${NIM_ENDPOINT_URL:-""}",
    "backend_endpoint": "${BACKEND_ENDPOINT_URL:-""}",
    "cluster_name": "${CLUSTER_NAME}",
    "instance_info": {}
}
EOF
}

# Pause EKS cluster (scale down nodes)
pause_eks_cluster() {
    echo -e "${BLUE}🔄 Pausing EKS Cluster...${NC}"
    
    if aws eks describe-cluster --name "$CLUSTER_NAME" &> /dev/null; then
        # Get current node group info
        NODE_GROUPS=$(aws eks list-nodegroups --cluster-name "$CLUSTER_NAME" --query 'nodegroups' --output text)
        
        if [ ! -z "$NODE_GROUPS" ] && [ "$NODE_GROUPS" != "None" ]; then
            for nodegroup in $NODE_GROUPS; do
                echo -e "${YELLOW}⏸️  Scaling down node group: $nodegroup${NC}"
                
                # Get current desired capacity
                CURRENT_CAPACITY=$(aws eks describe-nodegroup \
                    --cluster-name "$CLUSTER_NAME" \
                    --nodegroup-name "$nodegroup" \
                    --query 'nodegroup.scalingConfig.desiredSize' \
                    --output text)
                
                # Save current capacity for resume
                echo "EKS_NODEGROUP_${nodegroup}_CAPACITY=$CURRENT_CAPACITY" >> pause-state.env
                
                # Scale down to 0
                aws eks update-nodegroup-config \
                    --cluster-name "$CLUSTER_NAME" \
                    --nodegroup-name "$nodegroup" \
                    --scaling-config desiredSize=0,minSize=0,maxSize=2 &> /dev/null && \
                    echo -e "${GREEN}✅ Node group $nodegroup scaled down${NC}" || \
                    echo -e "${RED}❌ Failed to scale down $nodegroup${NC}"
            done
            ((RESOURCES_PAUSED++))
        else
            echo -e "${YELLOW}⚠️  No node groups found in cluster${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  EKS cluster $CLUSTER_NAME not found${NC}"
    fi
}

# Pause EC2 instances
pause_ec2_instances() {
    echo -e "${BLUE}🔄 Pausing EC2 Instances...${NC}"
    
    # Find running instances with our tags or names
    INSTANCE_IDS=$(aws ec2 describe-instances \
        --filters "Name=instance-state-name,Values=running" \
        --query 'Reservations[*].Instances[?Tags[?Key==`Name` && (contains(Value, `lumina`) || contains(Value, `backend`))]].[InstanceId]' \
        --output text)
    
    if [ ! -z "$INSTANCE_IDS" ] && [ "$INSTANCE_IDS" != "None" ]; then
        echo "EC2_INSTANCE_IDS=\"$INSTANCE_IDS\"" >> pause-state.env
        
        for instance_id in $INSTANCE_IDS; do
            echo -e "${YELLOW}⏸️  Stopping instance: $instance_id${NC}"
            
            aws ec2 stop-instances --instance-ids "$instance_id" &> /dev/null && \
                echo -e "${GREEN}✅ Instance $instance_id stopped${NC}" || \
                echo -e "${RED}❌ Failed to stop $instance_id${NC}"
        done
        ((RESOURCES_PAUSED++))
    else
        echo -e "${YELLOW}⚠️  No running EC2 instances found${NC}"
    fi
}

# Pause RDS instances (if any)
pause_rds_instances() {
    echo -e "${BLUE}🔄 Checking RDS Instances...${NC}"
    
    RDS_INSTANCES=$(aws rds describe-db-instances \
        --query 'DBInstances[?contains(DBInstanceIdentifier, `lumina`)].DBInstanceIdentifier' \
        --output text)
    
    if [ ! -z "$RDS_INSTANCES" ] && [ "$RDS_INSTANCES" != "None" ]; then
        echo "RDS_INSTANCE_IDS=\"$RDS_INSTANCES\"" >> pause-state.env
        
        for db_instance in $RDS_INSTANCES; do
            echo -e "${YELLOW}⏸️  Stopping RDS instance: $db_instance${NC}"
            
            aws rds stop-db-instance --db-instance-identifier "$db_instance" &> /dev/null && \
                echo -e "${GREEN}✅ RDS instance $db_instance stopped${NC}" || \
                echo -e "${RED}❌ Failed to stop $db_instance${NC}"
        done
        ((RESOURCES_PAUSED++))
    else
        echo -e "${YELLOW}⚠️  No RDS instances found${NC}"
    fi
}

# Save LoadBalancer endpoints before pausing
save_endpoints() {
    echo -e "${BLUE}💾 Saving endpoints...${NC}"
    
    # Save NIM endpoint if available
    if [ -f "nim-endpoint.env" ]; then
        cat nim-endpoint.env >> pause-state.env
    fi
    
    # Save backend endpoint if available
    if [ -f "backend-instance.env" ]; then
        cat backend-instance.env >> pause-state.env
    fi
    
    # Save EKS LoadBalancer info
    if kubectl get svc nim-public -n nim &> /dev/null; then
        EXTERNAL_IP=$(kubectl get svc nim-public -n nim -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
        if [ ! -z "$EXTERNAL_IP" ]; then
            echo "NIM_LOADBALANCER_ENDPOINT=$EXTERNAL_IP" >> pause-state.env
        fi
    fi
    
    echo -e "${GREEN}✅ Endpoints saved${NC}"
}

# Calculate cost savings
calculate_savings() {
    echo -e "${BLUE}💰 Calculating cost savings...${NC}"
    
    local hourly_savings=0
    
    # EKS node cost (g6e.xlarge ≈ $1.50/hour)
    if [ $RESOURCES_PAUSED -gt 0 ]; then
        hourly_savings=$(echo "$hourly_savings + 1.50" | bc -l 2>/dev/null || echo "1.50")
    fi
    
    # EC2 instance cost (g5.xlarge ≈ $1.50/hour)
    if [ ! -z "$INSTANCE_IDS" ]; then
        instance_count=$(echo "$INSTANCE_IDS" | wc -w)
        instance_savings=$(echo "$instance_count * 1.50" | bc -l 2>/dev/null || echo "1.50")
        hourly_savings=$(echo "$hourly_savings + $instance_savings" | bc -l 2>/dev/null || echo "3.00")
    fi
    
    echo "HOURLY_SAVINGS=$hourly_savings" >> pause-state.env
    echo -e "${GREEN}💰 Estimated savings: ~$${hourly_savings}/hour${NC}"
}

# Main pause execution
main() {
    create_pause_state
    
    # Initialize pause state file
    echo "# Lumina Pause State - $(date)" > pause-state.env
    echo "PAUSE_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> pause-state.env
    
    save_endpoints
    pause_eks_cluster
    pause_ec2_instances
    pause_rds_instances
    calculate_savings
    
    echo -e "${PURPLE}📊 Pause Summary${NC}"
    echo -e "${PURPLE}================${NC}"
    echo -e "${GREEN}Resources Paused: $RESOURCES_PAUSED${NC}"
    echo -e "${RED}Failed Operations: $RESOURCES_FAILED${NC}"
    
    if [ -f "pause-state.env" ]; then
        echo -e "${BLUE}💾 Pause state saved to: pause-state.env${NC}"
        echo -e "${YELLOW}📋 To resume: ./resume-system.sh${NC}"
        
        # Show what was paused
        echo -e "${BLUE}🔄 Paused Resources:${NC}"
        if grep -q "EKS_NODEGROUP" pause-state.env; then
            echo -e "   ✅ EKS cluster nodes scaled down"
        fi
        if grep -q "EC2_INSTANCE_IDS" pause-state.env; then
            echo -e "   ✅ EC2 instances stopped"
        fi
        if grep -q "RDS_INSTANCE_IDS" pause-state.env; then
            echo -e "   ✅ RDS instances stopped"
        fi
        
        # Show estimated savings
        if grep -q "HOURLY_SAVINGS" pause-state.env; then
            SAVINGS=$(grep "HOURLY_SAVINGS" pause-state.env | cut -d'=' -f2)
            echo -e "${GREEN}💰 Saving ~$${SAVINGS}/hour while paused${NC}"
        fi
    fi
    
    echo -e "${YELLOW}⚠️  Important Notes:${NC}"
    echo -e "   • LoadBalancer endpoints may change when resumed"
    echo -e "   • EKS pods will need to restart"
    echo -e "   • Allow 5-10 minutes for full resume"
    echo -e "   • Keep pause-state.env file safe for resuming"
}

# Handle different pause modes
case "${1:-}" in
    "quick")
        echo -e "${YELLOW}🚀 Quick pause (EC2 only)${NC}"
        create_pause_state
        echo "PAUSE_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > pause-state.env
        save_endpoints
        pause_ec2_instances
        ;;
    "eks")
        echo -e "${YELLOW}🚀 EKS pause only${NC}"
        create_pause_state
        echo "PAUSE_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > pause-state.env
        save_endpoints
        pause_eks_cluster
        ;;
    *)
        main
        ;;
esac

echo -e "${GREEN}⏸️  System paused successfully!${NC}"