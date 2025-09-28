#!/bin/bash
# ============================================================================
# AWS Elastic Beanstalk Environment Variables Setup Script
# ============================================================================
# This script sets environment variables for the EB application securely
# Uses AWS CLI instead of manual console configuration
# ============================================================================

set -e

# Configuration (must match your EB app)
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

# Function to check if environment exists
check_environment() {
    print_status "Checking if environment '$ENV_NAME' exists..."
    
    STATUS=$(aws elasticbeanstalk describe-environments \
        --environment-names "$ENV_NAME" \
        --region "$REGION" \
        --query "Environments[0].Status" \
        --output text 2>/dev/null || echo "None")
    
    if [ "$STATUS" = "None" ] || [ "$STATUS" = "null" ]; then
        print_error "Environment '$ENV_NAME' not found!"
        print_error "Please create the environment first or check the ENV_NAME configuration."
        exit 1
    fi
    
    print_success "Environment found with status: $STATUS"
}

# Function to prompt for secrets securely
get_secret() {
    local var_name=$1
    local prompt=$2
    
    echo -n "$prompt: "
    read -s value
    echo
    
    if [ -z "$value" ]; then
        print_error "$var_name cannot be empty!"
        exit 1
    fi
    
    echo "$value"
}

# Function to set environment variables
set_environment_variables() {
    print_status "Setting up environment variables..."
    
    # Get secrets from user input
    print_status "Please enter your API keys and credentials:"
    print_warning "Input will be hidden for security"
    echo
    
    TAVILY_API_KEY=$(get_secret "TAVILY_API_KEY" "Enter your Tavily API key")
    OPENAI_API_KEY=$(get_secret "OPENAI_API_KEY" "Enter your OpenAI API key")
    MONGODB_CONNECTION_STRING=$(get_secret "MONGODB_CONNECTION_STRING" "Enter your MongoDB connection string")
    
    echo
    print_status "Setting environment variables via AWS CLI..."
    
    # Create the environment variables JSON
    ENV_VARS=$(cat <<EOF
[
    {
        "Namespace": "aws:elasticbeanstalk:application:environment",
        "OptionName": "TAVILY_API_KEY",
        "Value": "$TAVILY_API_KEY"
    },
    {
        "Namespace": "aws:elasticbeanstalk:application:environment",
        "OptionName": "OPENAI_API_KEY", 
        "Value": "$OPENAI_API_KEY"
    },
    {
        "Namespace": "aws:elasticbeanstalk:application:environment",
        "OptionName": "MONGODB_CONNECTION_STRING",
        "Value": "$MONGODB_CONNECTION_STRING"
    },
    {
        "Namespace": "aws:elasticbeanstalk:application:environment",
        "OptionName": "DATABASE_NAME",
        "Value": "web_research_agent"
    },
    {
        "Namespace": "aws:elasticbeanstalk:application:environment",
        "OptionName": "CORS_ORIGINS",
        "Value": "http://localhost:3000,https://dgbfif5o7v03y.cloudfront.net"
    }
]
EOF
)

    # Update the environment with new variables
    aws elasticbeanstalk update-environment \
        --environment-name "$ENV_NAME" \
        --region "$REGION" \
        --option-settings "$ENV_VARS" \
        --output table
    
    if [ $? -eq 0 ]; then
        print_success "Environment variables updated successfully!"
        print_status "The environment is now updating. This may take a few minutes."
        print_status "You can monitor progress in the AWS console or with:"
        echo "aws elasticbeanstalk describe-environments --environment-names $ENV_NAME --region $REGION"
    else
        print_error "Failed to update environment variables!"
        exit 1
    fi
}

# Function to display current environment variables (non-sensitive ones)
show_current_vars() {
    print_status "Current non-sensitive environment variables:"
    
    aws elasticbeanstalk describe-configuration-settings \
        --application-name "$APP_NAME" \
        --environment-name "$ENV_NAME" \
        --region "$REGION" \
        --query "ConfigurationSettings[0].OptionSettings[?Namespace=='aws:elasticbeanstalk:application:environment' && !contains(OptionName, 'KEY') && !contains(OptionName, 'STRING')].{Name:OptionName,Value:Value}" \
        --output table
}

# Main execution
main() {
    echo "============================================================================"
    echo "🔧 Elastic Beanstalk Environment Variables Setup"
    echo "============================================================================"
    echo "App Name: $APP_NAME"
    echo "Environment: $ENV_NAME"
    echo "Region: $REGION"
    echo "============================================================================"
    echo
    
    # Check AWS CLI is configured
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH!"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured! Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured and authenticated"
    
    # Check if environment exists
    check_environment
    
    # Show current non-sensitive vars
    show_current_vars
    
    echo
    print_warning "This will update environment variables for $ENV_NAME"
    echo -n "Continue? (y/N): "
    read -r confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_status "Operation cancelled."
        exit 0
    fi
    
    # Set the environment variables
    set_environment_variables
    
    echo
    print_success "✅ Environment variables setup complete!"
    print_status "Your EB environment is now updating with the new configuration."
    print_status "Check the AWS console or use eb status to monitor progress."
}

# Run the main function
main "$@"
