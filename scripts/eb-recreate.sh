#!/bin/bash
# ============================================================================
# AWS Elastic Beanstalk Recreation Script
# ============================================================================
# This script recreates the exact same environment after termination
# Maintains the SAME URL: cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com
# ============================================================================

set -e

# Configuration
APP_NAME="cognitive-core"
ENV_NAME="cognitive-core-fresh"
PLATFORM="Python 3.12 running on 64bit Amazon Linux 2023"
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

print_status "🚀 Recreating Elastic Beanstalk Environment"
print_status "Environment: $ENV_NAME"
print_status "Platform: $PLATFORM"
print_warning "💰 This will cost ~$30/month when running"
echo ""

# Check if environment already exists
print_status "Checking current environment status..."
STATUS=$(aws elasticbeanstalk describe-environments \
    --application-name "$APP_NAME" \
    --environment-names "$ENV_NAME" \
    --region "$REGION" \
    --query 'Environments[0].Status' \
    --output text 2>/dev/null || echo "NotFound")

case $STATUS in
    "Ready")
        print_success "Environment is already running! ✅"
        print_status "URL: http://$ENV_NAME.eba-c4n432jt.us-east-1.elasticbeanstalk.com"
        exit 0
        ;;
    "Launching"|"Updating")
        print_warning "Environment is already being created/updated..."
        print_status "Waiting for it to complete..."
        ;;
    "Terminated"|"NotFound")
        print_status "Environment is terminated/not found - ready to recreate"
        ;;
    *)
        print_warning "Environment status: $STATUS"
        ;;
esac

# Create the environment
print_status "Creating environment with eb create..."
eb create "$ENV_NAME" \
    --platform "$PLATFORM" \
    --instance-type t3.micro \
    --region "$REGION" \
    --cname "$ENV_NAME"

# Wait for environment to be ready
print_status "Environment creation initiated..."
print_status "This will take 3-5 minutes..."

# Check final status
print_status "Checking final status..."
eb status "$ENV_NAME"

# Test the endpoint
print_status "Testing the recreated endpoint..."
sleep 30  # Give it a moment to start serving

# Get the actual CNAME from EB for testing
ACTUAL_CNAME=$(eb status "$ENV_NAME" --region "$REGION" | grep "CNAME:" | awk '{print $2}')
print_status "Testing URL: http://$ACTUAL_CNAME/health"

curl -f "http://$ACTUAL_CNAME/health" || {
    print_warning "Health check failed, but environment might still be starting up"
}

# Get the actual CNAME from EB
ACTUAL_CNAME=$(eb status "$ENV_NAME" --region "$REGION" | grep "CNAME:" | awk '{print $2}')

print_success "🎉 Environment recreation complete!"
print_success "URL: http://$ACTUAL_CNAME"
print_warning "💰 Now costing ~$30/month"
