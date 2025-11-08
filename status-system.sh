#!/bin/bash

# Lumina System Status Script
# Shows current status of all AWS resources

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}📊 Lumina System Status${NC}"
echo -e "${PURPLE}=======================${NC}"

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
RUNNING_RESOURCES=0
STOPPED_RESOURCES=0
TOTAL_COST_PER_HOUR=0

# Function to check resource status
check_resource_status() {
    local resource_name="$1"
    local status="$2"
    local cost_per_hour="$3"
    
    if [ "$status" = "running" ] || [ "$status" = "available" ] || [ "$status" = "active" ]; then
        echo -e "${GREEN}✅ $resource_name: $status${NC}"
        ((RUNNING_RESOURCES++))
        TOTAL_COST_PER_HOUR=$(echo "$TOTAL_COST_PER_HOUR + $cost_per_hour" | bc -l 2>/dev/null || echo "$TOTAL_COST_PER_HOUR")
    elif [ "$status" = "stopped" ] || [ "$status" = "inactive" ] || [ "$status" = "scaled-down" ]; then
        echo -e "${YELLOW}⏸️  $resource_name: $status${NC}"
        ((STOPPED_RESOURCES++))
    else
        echo -e "${RED}❌ $resource_name: $status${NC}"
    fi
}

# Check EKS cluster status
check_eks_status() {
    echo -e "${BLUE}🔄 EKS Cluster Status${NC}"
    
    if aws eks describe-cluster --name "$CLUSTER_NAME" &> /dev/null; then
        CLUSTER_STATUS=$(aws eks describe-cluster --name "$CLUSTER_NAME" --query 'cluster.status' --output text)
        echo -e "${GREEN}✅ Cluster $CLUSTER_NAME: $CLUSTER_STATUS${NC}"
        
        # Check node groups
        NODE_GROUPS=$(aws eks list-nodegroups --cluster-name "$CLUSTER_NAME" --query 'nodegroups' --output text)
        
        if [ ! -z "$NODE_GROUPS" ] && [ "$NODE_GROUPS" != "None" ]; then
            for nodegroup in $NODE_GROUPS; do
                DESIRED_SIZE=$(aws eks describe-nodegroup \
                    --cluster-name "$CLUSTER_NAME" \
                    --nodegroup-name "$nodegroup" \
                    --query 'nodegroup.scalingConfig.desiredSize' \
                    --output text)
                
                CURRENT_SIZE=$(aws eks describe-nodegroup \
                    --cluster-name "$CLUSTER_NAME" \
                    --nodegroup-name "$nodegroup" \
                    --query 'nodegroup.status' \
                    --output text)
                
                if [ "$DESIRED_SIZE" -gt 0 ]; then
                    check_resource_status "Node Group $nodegroup ($DESIRED_SIZE nodes)" "running" "1.50"
                else
                    check_resource_status "Node Group $nodegroup" "scaled-down" "0"
                fi
            done
        fi
        
        # Check pods in nim namespace
        if kubectl get namespace nim &> /dev/null; then
            echo -e "${BLUE}🤖 NIM Pods Status${NC}"
            kubectl get pods -n nim --no-headers 2>/dev/null | while read line; do
                if [ ! -z "$line" ]; then
                    POD_NAME=$(echo $line | awk '{print $1}')
                    POD_STATUS=$(echo $line | awk '{print $3}')
                    echo -e "${YELLOW}   Pod $POD_NAME: $POD_STATUS${NC}"
                fi
            done
        fi
        
        # Check services
        if kubectl get svc nim-public -n nim &> /dev/null; then
            EXTERNAL_IP=$(kubectl get svc nim-public -n nim -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
            if [ "$EXTERNAL_IP" != "pending" ] && [ ! -z "$EXTERNAL_IP" ]; then
                echo -e "${GREEN}✅ NIM LoadBalancer: http://$EXTERNAL_IP:8000${NC}"
            else
                echo -e "${YELLOW}⏳ NIM LoadBalancer: pending${NC}"
            fi
        fi
        
    else
        echo -e "${RED}❌ EKS cluster $CLUSTER_NAME not found${NC}"
    fi
}

# Check EC2 instances status
check_ec2_status() {
    echo -e "${BLUE}🖥️  EC2 Instances Status${NC}"
    
    # Find instances with lumina or backend tags
    INSTANCES=$(aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=*lumina*,*backend*" \
        --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
        --output text 2>/dev/null)
    
    if [ ! -z "$INSTANCES" ]; then
        echo "$INSTANCES" | while read instance_id state instance_type public_ip name; do
            if [ ! -z "$instance_id" ]; then
                # Calculate cost based on instance type
                case "$instance_type" in
                    "g5.xlarge") cost="1.50" ;;
                    "g6e.xlarge") cost="1.50" ;;
                    "t3.medium") cost="0.05" ;;
                    *) cost="1.00" ;;
                esac
                
                if [ "$state" = "running" ]; then
                    echo -e "${GREEN}✅ $name ($instance_id): $state - $public_ip${NC}"
                    TOTAL_COST_PER_HOUR=$(echo "$TOTAL_COST_PER_HOUR + $cost" | bc -l 2>/dev/null || echo "$TOTAL_COST_PER_HOUR")
                    ((RUNNING_RESOURCES++))
                else
                    echo -e "${YELLOW}⏸️  $name ($instance_id): $state${NC}"
                    ((STOPPED_RESOURCES++))
                fi
            fi
        done
    else
        echo -e "${YELLOW}⚠️  No EC2 instances found with lumina/backend tags${NC}"
    fi
}

# Check RDS instances status
check_rds_status() {
    echo -e "${BLUE}🗄️  RDS Instances Status${NC}"
    
    RDS_INSTANCES=$(aws rds describe-db-instances \
        --query 'DBInstances[?contains(DBInstanceIdentifier, `lumina`)].[DBInstanceIdentifier,DBInstanceStatus,DBInstanceClass]' \
        --output text 2>/dev/null)
    
    if [ ! -z "$RDS_INSTANCES" ]; then
        echo "$RDS_INSTANCES" | while read db_id status instance_class; do
            if [ ! -z "$db_id" ]; then
                # Calculate cost based on instance class
                case "$instance_class" in
                    "db.t3.micro") cost="0.02" ;;
                    "db.t3.small") cost="0.04" ;;
                    *) cost="0.10" ;;
                esac
                
                check_resource_status "RDS $db_id" "$status" "$cost"
            fi
        done
    else
        echo -e "${YELLOW}⚠️  No RDS instances found${NC}"
    fi
}

# Check S3 buckets
check_s3_status() {
    echo -e "${BLUE}🪣 S3 Buckets Status${NC}"
    
    S3_BUCKETS=$(aws s3 ls | grep lumina | awk '{print $3}' 2>/dev/null)
    
    if [ ! -z "$S3_BUCKETS" ]; then
        echo "$S3_BUCKETS" | while read bucket; do
            if [ ! -z "$bucket" ]; then
                # Check if bucket has website configuration
                if aws s3api get-bucket-website --bucket "$bucket" &> /dev/null; then
                    WEBSITE_URL="http://$bucket.s3-website-$AWS_DEFAULT_REGION.amazonaws.com"
                    echo -e "${GREEN}✅ S3 Website $bucket: $WEBSITE_URL${NC}"
                else
                    echo -e "${GREEN}✅ S3 Bucket $bucket: active${NC}"
                fi
                # S3 cost is minimal for demo purposes
                TOTAL_COST_PER_HOUR=$(echo "$TOTAL_COST_PER_HOUR + 0.01" | bc -l 2>/dev/null || echo "$TOTAL_COST_PER_HOUR")
            fi
        done
    else
        echo -e "${YELLOW}⚠️  No S3 buckets found with lumina prefix${NC}"
    fi
}

# Check endpoints connectivity
check_endpoints() {
    echo -e "${BLUE}🔗 Endpoint Connectivity${NC}"
    
    # Check NIM endpoint
    if [ -f "nim-endpoint.env" ]; then
        source nim-endpoint.env
        echo -e "${YELLOW}Testing NIM endpoint: $NIM_ENDPOINT_URL${NC}"
        if curl -s --max-time 5 "$NIM_ENDPOINT_URL/v1/models" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ NIM API: responding${NC}"
        else
            echo -e "${RED}❌ NIM API: not responding${NC}"
        fi
    fi
    
    # Check backend endpoint
    if [ -f "backend-instance.env" ]; then
        source backend-instance.env
        echo -e "${YELLOW}Testing backend endpoint: $BACKEND_ENDPOINT_URL${NC}"
        if curl -s --max-time 5 "$BACKEND_ENDPOINT_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend API: responding${NC}"
        else
            echo -e "${RED}❌ Backend API: not responding${NC}"
        fi
    fi
    
    # Check resumed endpoints
    if [ -f "nim-endpoint-resumed.env" ]; then
        source nim-endpoint-resumed.env
        echo -e "${YELLOW}Testing resumed NIM endpoint: $NIM_ENDPOINT_URL${NC}"
        if curl -s --max-time 5 "$NIM_ENDPOINT_URL/v1/models" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Resumed NIM API: responding${NC}"
        else
            echo -e "${RED}❌ Resumed NIM API: not responding${NC}"
        fi
    fi
    
    if [ -f "backend-instance-resumed.env" ]; then
        source backend-instance-resumed.env
        echo -e "${YELLOW}Testing resumed backend endpoint: $BACKEND_ENDPOINT_URL${NC}"
        if curl -s --max-time 5 "$BACKEND_ENDPOINT_URL/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Resumed Backend API: responding${NC}"
        else
            echo -e "${RED}❌ Resumed Backend API: not responding${NC}"
        fi
    fi
}

# Show pause state if exists
check_pause_state() {
    if [ -f "pause-state.env" ]; then
        echo -e "${BLUE}⏸️  Pause State Information${NC}"
        source pause-state.env
        
        if [ ! -z "$PAUSE_TIMESTAMP" ]; then
            echo -e "${YELLOW}   Last paused: $PAUSE_TIMESTAMP${NC}"
            
            # Calculate time since pause
            PAUSE_EPOCH=$(date -d "$PAUSE_TIMESTAMP" +%s 2>/dev/null || echo "0")
            CURRENT_EPOCH=$(date +%s)
            HOURS_SINCE_PAUSE=$(echo "scale=1; ($CURRENT_EPOCH - $PAUSE_EPOCH) / 3600" | bc -l 2>/dev/null || echo "unknown")
            
            if [ "$HOURS_SINCE_PAUSE" != "unknown" ]; then
                echo -e "${YELLOW}   Time since pause: ${HOURS_SINCE_PAUSE}h${NC}"
            fi
        fi
        
        if [ ! -z "$HOURLY_SAVINGS" ]; then
            echo -e "${YELLOW}   Estimated hourly savings when paused: $${HOURLY_SAVINGS}${NC}"
        fi
    fi
}

# Main status check
main() {
    check_eks_status
    echo
    check_ec2_status
    echo
    check_rds_status
    echo
    check_s3_status
    echo
    check_endpoints
    echo
    check_pause_state
    
    echo -e "${PURPLE}📊 System Summary${NC}"
    echo -e "${PURPLE}=================${NC}"
    echo -e "${GREEN}Running Resources: $RUNNING_RESOURCES${NC}"
    echo -e "${YELLOW}Stopped Resources: $STOPPED_RESOURCES${NC}"
    
    if [ $(echo "$TOTAL_COST_PER_HOUR > 0" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
        echo -e "${BLUE}💰 Current hourly cost: ~$${TOTAL_COST_PER_HOUR}${NC}"
        
        DAILY_COST=$(echo "$TOTAL_COST_PER_HOUR * 24" | bc -l 2>/dev/null || echo "0")
        echo -e "${BLUE}💰 Estimated daily cost: ~$${DAILY_COST}${NC}"
    else
        echo -e "${GREEN}💰 Current hourly cost: $0 (all resources paused)${NC}"
    fi
    
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo -e "   ./pause-system.sh     - Pause all resources"
    echo -e "   ./resume-system.sh    - Resume all resources"
    echo -e "   ./status-system.sh    - Show this status"
    echo -e "   ./validate-setup.sh   - Validate configuration"
}

# Handle different status modes
case "${1:-}" in
    "watch")
        echo -e "${YELLOW}👀 Watching system status (Ctrl+C to exit)${NC}"
        while true; do
            clear
            main
            echo -e "${YELLOW}Refreshing in 30 seconds...${NC}"
            sleep 30
        done
        ;;
    "quick")
        check_endpoints
        ;;
    *)
        main
        ;;
esac