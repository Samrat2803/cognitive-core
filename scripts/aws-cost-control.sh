#!/bin/bash

###############################################################################
# AWS Cost Control - Automatic Resource Cleanup
###############################################################################
# This script helps identify and optionally delete high-cost AWS resources
# that are older than X days or unused.
###############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DAYS_THRESHOLD=${AWS_CLEANUP_DAYS:-30}  # Default: 30 days
DRY_RUN=${DRY_RUN:-true}  # Default: dry run (don't delete)

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        AWS COST CONTROL - RESOURCE CLEANUP                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  • Days threshold: ${DAYS_THRESHOLD} days"
echo -e "  • Dry run: ${DRY_RUN} (set DRY_RUN=false to actually delete)"
echo ""

# Calculate date threshold
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    THRESHOLD_DATE=$(date -v-${DAYS_THRESHOLD}d -u +"%Y-%m-%dT%H:%M:%S")
else
    # Linux
    THRESHOLD_DATE=$(date -d "${DAYS_THRESHOLD} days ago" -u +"%Y-%m-%dT%H:%M:%S")
fi

echo -e "${BLUE}Resources older than: ${THRESHOLD_DATE}${NC}"
echo ""

###############################################################################
# 1. CHECK ELASTIC BEANSTALK ENVIRONMENTS
###############################################################################
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}1️⃣  ELASTIC BEANSTALK ENVIRONMENTS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OLD_ENVS=$(aws elasticbeanstalk describe-environments \
    --query "Environments[?DateCreated<'${THRESHOLD_DATE}' && Status!='Terminated'].{Name:EnvironmentName,Created:DateCreated,Status:Status}" \
    --output json)

if [ "$OLD_ENVS" == "[]" ]; then
    echo -e "${GREEN}✅ No old EB environments found${NC}"
else
    echo "$OLD_ENVS" | jq -r '.[] | "⚠️  \(.Name) - Created: \(.Created) - Status: \(.Status)"'
    
    if [ "$DRY_RUN" == "false" ]; then
        echo ""
        echo -e "${RED}Would you like to terminate these environments? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "$OLD_ENVS" | jq -r '.[].Name' | while read env_name; do
                echo -e "${YELLOW}Terminating: $env_name${NC}"
                aws elasticbeanstalk terminate-environment --environment-name "$env_name" --terminate-resources
            done
        fi
    fi
fi

echo ""

###############################################################################
# 2. CHECK UNUSED LOAD BALANCERS
###############################################################################
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}2️⃣  APPLICATION LOAD BALANCERS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

OLD_ALBS=$(aws elbv2 describe-load-balancers \
    --query "LoadBalancers[?CreatedTime<'${THRESHOLD_DATE}'].{Name:LoadBalancerName,Created:CreatedTime,ARN:LoadBalancerArn}" \
    --output json 2>/dev/null || echo "[]")

if [ "$OLD_ALBS" == "[]" ]; then
    echo -e "${GREEN}✅ No old load balancers found${NC}"
else
    echo "$OLD_ALBS" | jq -r '.[] | "💰 \(.Name) - Created: \(.Created) (~$16/month)"'
    echo ""
    echo -e "${YELLOW}💡 Note: Load balancers cost ~\$16/month. Consider removing if unused.${NC}"
fi

echo ""

###############################################################################
# 3. CHECK S3 BUCKETS
###############################################################################
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}3️⃣  S3 BUCKETS (with lifecycle policies)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

BUCKETS=$(aws s3 ls | awk '{print $3}')

for bucket in $BUCKETS; do
    # Get lifecycle configuration
    LIFECYCLE=$(aws s3api get-bucket-lifecycle-configuration --bucket "$bucket" 2>/dev/null || echo "none")
    
    # Get bucket size
    SIZE=$(aws s3 ls s3://$bucket --recursive --summarize 2>/dev/null | grep "Total Size" | awk '{print $3}')
    SIZE_MB=$(echo "scale=2; $SIZE / 1024 / 1024" | bc 2>/dev/null || echo "0")
    
    if [ "$LIFECYCLE" == "none" ]; then
        echo -e "${YELLOW}⚠️  $bucket - ${SIZE_MB}MB - NO lifecycle policy${NC}"
    else
        echo -e "${GREEN}✅ $bucket - ${SIZE_MB}MB - Has lifecycle policy${NC}"
    fi
done

echo ""

###############################################################################
# 4. CHECK CLOUDFRONT DISTRIBUTIONS
###############################################################################
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}4️⃣  CLOUDFRONT DISTRIBUTIONS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DISTRIBUTIONS=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[].{ID:Id,Domain:DomainName,Status:Status,Enabled:Enabled}" \
    --output json 2>/dev/null || echo "[]")

if [ "$DISTRIBUTIONS" == "[]" ]; then
    echo -e "${GREEN}✅ No CloudFront distributions found${NC}"
else
    echo "$DISTRIBUTIONS" | jq -r '.[] | "📡 \(.Domain) - Status: \(.Status) - Enabled: \(.Enabled)"'
    echo ""
    echo -e "${YELLOW}💡 CloudFront cost is traffic-based (~\$1-5/month per distribution)${NC}"
fi

echo ""

###############################################################################
# 5. CHECK EC2 INSTANCES (Standalone)
###############################################################################
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}5️⃣  EC2 INSTANCES (Standalone, not managed by EB)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

STANDALONE_INSTANCES=$(aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query "Reservations[].Instances[?!contains(Tags[?Key=='elasticbeanstalk:environment-name'].Value, 'political-analyst')].{ID:InstanceId,Type:InstanceType,LaunchTime:LaunchTime}" \
    --output json 2>/dev/null || echo "[]")

if [ "$STANDALONE_INSTANCES" == "[]" ]; then
    echo -e "${GREEN}✅ No standalone EC2 instances found${NC}"
else
    echo "$STANDALONE_INSTANCES" | jq -r '.[] | "💻 \(.ID) - Type: \(.Type) - Launched: \(.LaunchTime)"'
fi

echo ""

###############################################################################
# COST SUMMARY
###############################################################################
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    COST SUMMARY                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Get current month's estimated charges
CURRENT_COST=$(aws cloudwatch get-metric-statistics \
    --namespace AWS/Billing \
    --metric-name EstimatedCharges \
    --dimensions Name=Currency,Value=USD \
    --start-time $(date -u -d '5 days ago' +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -u -v-5d +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 86400 \
    --statistics Maximum \
    --query 'Datapoints[0].Maximum' \
    --output text 2>/dev/null || echo "N/A")

echo -e "${YELLOW}Current month estimated cost: \$${CURRENT_COST}${NC}"
echo ""

###############################################################################
# RECOMMENDATIONS
###############################################################################
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}💡 RECOMMENDATIONS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "1. Set up AWS Budget Alerts:"
echo "   aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget file://budget.json"
echo ""
echo "2. Enable Cost Anomaly Detection:"
echo "   https://console.aws.amazon.com/cost-management/home#/anomaly-detection"
echo ""
echo "3. Review unused resources monthly:"
echo "   Run this script: ./scripts/aws-cost-control.sh"
echo ""
echo "4. To actually delete resources (not dry run):"
echo "   DRY_RUN=false AWS_CLEANUP_DAYS=30 ./scripts/aws-cost-control.sh"
echo ""

echo -e "${GREEN}✅ Cost control check complete!${NC}"

