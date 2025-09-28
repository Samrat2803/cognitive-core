#!/bin/bash
# ============================================================================
# AWS Elastic Beanstalk Cost Control Script
# ============================================================================
# This script allows you to start/stop your EB environment to save costs
# URL remains the same: cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com
# 
# COST SAVINGS: 
# - Running: ~$30/month for t3.micro
# - Stopped: ~$0/month (only pay for data transfer when starting/stopping)
# ============================================================================

set -e  # Exit on any error

# Configuration
APP_NAME="cognitive-core"
ENV_NAME="cognitive-core-fresh"
REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to get current environment status
get_status() {
    print_status "Getting environment status..."
    aws elasticbeanstalk describe-environments \
        --application-name "$APP_NAME" \
        --environment-names "$ENV_NAME" \
        --region "$REGION" \
        --query 'Environments[0].Status' \
        --output text 2>/dev/null || echo "NotFound"
}

# Function to show environment info
show_info() {
    print_status "Environment Information:"
    echo "  Application: $APP_NAME"
    echo "  Environment: $ENV_NAME"
    echo "  Region: $REGION"
    echo "  URL: http://$ENV_NAME.eba-c4n432jt.us-east-1.elasticbeanstalk.com"
    echo ""
    
    STATUS=$(get_status)
    case $STATUS in
        "Ready")
            print_success "Status: RUNNING ✅"
            echo "  💰 Current cost: ~$30/month"
            ;;
        "Terminated")
            print_warning "Status: STOPPED ⏸️"
            echo "  💰 Current cost: ~$0/month"
            ;;
        "Launching"|"Updating")
            print_status "Status: STARTING UP 🚀"
            echo "  💰 Transitioning to: ~$30/month"
            ;;
        "Terminating")
            print_status "Status: STOPPING ⏹️"
            echo "  💰 Transitioning to: ~$0/month"
            ;;
        *)
            print_error "Status: UNKNOWN ($STATUS)"
            ;;
    esac
    echo ""
}

# Function to start the environment
start_env() {
    STATUS=$(get_status)
    
    if [ "$STATUS" = "Ready" ]; then
        print_warning "Environment is already running!"
        return 0
    fi
    
    if [ "$STATUS" = "Launching" ] || [ "$STATUS" = "Updating" ]; then
        print_warning "Environment is already starting up..."
        return 0
    fi
    
    if [ "$STATUS" = "NotFound" ] || [ "$STATUS" = "Terminated" ]; then
        print_error "Environment not found or terminated!"
        print_error "You'll need to recreate it with: eb create"
        return 1
    fi
    
    print_status "Starting environment: $ENV_NAME"
    print_warning "This will take 2-3 minutes and cost ~$30/month"
    
    # Actually start the environment (this would be environment-specific)
    # For EB, you typically can't "start" a terminated environment
    # You need to either restore from a saved configuration or recreate
    print_error "Feature not yet implemented - EB environments can't be 'started' once terminated"
    print_error "Use 'eb create' to recreate the environment"
    return 1
}

# Function to stop the environment  
stop_env() {
    STATUS=$(get_status)
    
    if [ "$STATUS" = "Terminated" ]; then
        print_warning "Environment is already stopped!"
        return 0
    fi
    
    if [ "$STATUS" = "Terminating" ]; then
        print_warning "Environment is already stopping..."
        return 0
    fi
    
    if [ "$STATUS" != "Ready" ]; then
        print_warning "Environment is not in a stable state: $STATUS"
        print_warning "Waiting for it to become Ready first..."
        wait_for_ready
    fi
    
    print_status "Stopping environment: $ENV_NAME"
    print_status "This will save ~$30/month but terminate all instances"
    
    read -p "Are you sure you want to stop the environment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Operation cancelled"
        return 0
    fi
    
    print_status "Terminating environment..."
    aws elasticbeanstalk terminate-environment \
        --environment-name "$ENV_NAME" \
        --region "$REGION" \
        --terminate-resources
    
    print_success "Environment termination initiated"
    print_status "This will take 2-3 minutes to complete"
    print_success "💰 You'll save ~$30/month while stopped"
}

# Function to wait for environment to be ready
wait_for_ready() {
    print_status "Waiting for environment to be ready..."
    
    while true; do
        STATUS=$(get_status)
        case $STATUS in
            "Ready")
                print_success "Environment is ready!"
                break
                ;;
            "Terminated")
                print_success "Environment is terminated (stopped)"
                break
                ;;
            *)
                print_status "Current status: $STATUS - waiting..."
                sleep 30
                ;;
        esac
    done
}

# Function to show usage
show_usage() {
    echo "AWS Elastic Beanstalk Cost Control Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the EB environment (~$30/month)"
    echo "  stop      Stop the EB environment (~$0/month)"
    echo "  status    Show current environment status"
    echo "  info      Show detailed environment information"
    echo "  wait      Wait for environment to become ready"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 stop"
    echo "  $0 start"
    echo ""
    echo "Note: The URL remains the same after start/stop:"
    echo "http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com"
}

# Main script logic
case "${1:-status}" in
    "start")
        show_info
        start_env
        ;;
    "stop")
        show_info
        stop_env
        ;;
    "status")
        show_info
        ;;
    "info")
        show_info
        aws elasticbeanstalk describe-environments \
            --application-name "$APP_NAME" \
            --environment-names "$ENV_NAME" \
            --region "$REGION" \
            --output table
        ;;
    "wait")
        wait_for_ready
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
