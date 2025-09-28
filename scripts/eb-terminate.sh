#!/bin/bash
# ============================================================================
# AWS Elastic Beanstalk Termination Script  
# ============================================================================
# This script safely terminates the EB environment to save costs
# SAVES: ~$30/month when terminated
# ============================================================================

set -e

# Configuration
APP_NAME="cognitive-core"
ENV_NAME="cognitive-core-fresh"
REGION="us-east-1"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

print_warning "⚠️  ENVIRONMENT TERMINATION"
print_status "Environment: $ENV_NAME"
print_success "💰 Will save: ~$30/month"
print_warning "⚠️  All data and instances will be terminated"
echo ""

# Check current status
STATUS=$(aws elasticbeanstalk describe-environments \
    --application-name "$APP_NAME" \
    --environment-names "$ENV_NAME" \
    --region "$REGION" \
    --query 'Environments[0].Status' \
    --output text 2>/dev/null || echo "NotFound")

case $STATUS in
    "Terminated"|"NotFound")
        print_success "Environment is already terminated! 💰"
        print_success "You're already saving ~$30/month"
        exit 0
        ;;
    "Terminating")
        print_warning "Environment is already being terminated..."
        print_status "Waiting for completion..."
        ;;
    "Ready")
        print_status "Environment is running - ready to terminate"
        ;;
    *)
        print_warning "Environment status: $STATUS"
        print_warning "Will attempt to terminate anyway..."
        ;;
esac

# Confirmation
echo ""
print_warning "🚨 CONFIRMATION REQUIRED:"
echo "  • Environment: $ENV_NAME"
echo "  • Current cost: ~$30/month"
echo "  • After termination: ~$0/month"
echo "  • URL will be unavailable until recreation"
echo "  • Recreation takes 3-5 minutes"
echo ""
read -p "$(echo -e ${RED})Are you sure you want to terminate? (type 'yes' to confirm): ${NC}" -r
echo ""

if [ "$REPLY" != "yes" ]; then
    print_status "Termination cancelled - environment remains running"
    exit 0
fi

# Terminate the environment
print_status "Terminating environment..."
eb terminate "$ENV_NAME" --force

print_success "🎉 Environment termination initiated!"
print_success "💰 You'll save ~$30/month while terminated"
print_status "📝 To recreate later, use: ./scripts/eb-recreate.sh"
print_status "🔗 Same URL will be restored: http://$ENV_NAME.eba-c4n432jt.us-east-1.elasticbeanstalk.com"
