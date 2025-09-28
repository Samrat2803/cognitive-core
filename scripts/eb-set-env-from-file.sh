#!/bin/bash
# ============================================================================
# AWS Elastic Beanstalk Environment Variables from File Script
# ============================================================================
# This script reads environment variables from a secure .env file
# WARNING: Only use this for automation - keep .env files secure and private!
# ============================================================================

set -e

# Configuration
APP_NAME="cognitive-core"
ENV_NAME="cognitive-core-fresh"
REGION="us-east-1"

# Default .env file location (outside of git repo for security)
DEFAULT_ENV_FILE="$HOME/.aws/eb-secrets-${ENV_NAME}.env"

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

# Function to create example .env file
create_example_env() {
    local env_file=$1
    
    cat > "$env_file" << 'EOF'
# Elastic Beanstalk Environment Variables
# WARNING: This file contains secrets - keep it secure!

# API Keys
TAVILY_API_KEY=tvly-dev-YOUR_TAVILY_API_KEY_HERE
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE

# Database
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster0.example.mongodb.net/?retryWrites=true&w=majority&appName=YourAppName

# These are set automatically by the script:
# DATABASE_NAME=web_research_agent
# CORS_ORIGINS=http://localhost:3000,https://dgbfif5o7v03y.cloudfront.net
EOF

    print_success "Created example env file: $env_file"
    print_warning "Please edit this file with your actual credentials before running the script again."
}

# Function to load and validate .env file
load_env_file() {
    local env_file=$1
    
    if [[ ! -f "$env_file" ]]; then
        print_error "Environment file not found: $env_file"
        print_status "Creating example file for you..."
        mkdir -p "$(dirname "$env_file")"
        create_example_env "$env_file"
        exit 1
    fi
    
    print_status "Loading environment variables from: $env_file"
    
    # Source the .env file
    set -a  # automatically export all variables
    source "$env_file"
    set +a  # stop automatically exporting
    
    # Validate required variables
    local required_vars=("TAVILY_API_KEY" "OPENAI_API_KEY" "MONGODB_CONNECTION_STRING")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" || "${!var}" == *"YOUR_"*"_HERE" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_error "Missing or placeholder values for required variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please update $env_file with actual values."
        exit 1
    fi
    
    print_success "All required environment variables loaded successfully"
}

# Function to set environment variables
set_environment_variables() {
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

    # Update the environment
    aws elasticbeanstalk update-environment \
        --environment-name "$ENV_NAME" \
        --region "$REGION" \
        --option-settings "$ENV_VARS" \
        --output table
    
    if [ $? -eq 0 ]; then
        print_success "Environment variables updated successfully!"
        print_status "The environment is now updating. This may take a few minutes."
    else
        print_error "Failed to update environment variables!"
        exit 1
    fi
}

# Main execution
main() {
    local env_file="${1:-$DEFAULT_ENV_FILE}"
    
    echo "============================================================================"
    echo "🔧 Elastic Beanstalk Environment Variables from File"
    echo "============================================================================"
    echo "App Name: $APP_NAME"
    echo "Environment: $ENV_NAME"
    echo "Region: $REGION"
    echo "Env File: $env_file"
    echo "============================================================================"
    echo
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed!"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured! Please run 'aws configure' first."
        exit 1
    fi
    
    # Load environment file
    load_env_file "$env_file"
    
    # Confirm before proceeding
    echo
    print_warning "This will update environment variables for $ENV_NAME"
    echo -n "Continue? (y/N): "
    read -r confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_status "Operation cancelled."
        exit 0
    fi
    
    # Set the variables
    set_environment_variables
    
    print_success "✅ Environment variables updated from file!"
}

# Show usage if help requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [env-file]"
    echo
    echo "Sets Elastic Beanstalk environment variables from a .env file"
    echo
    echo "Arguments:"
    echo "  env-file    Path to .env file (default: $DEFAULT_ENV_FILE)"
    echo
    echo "Examples:"
    echo "  $0                                    # Use default file"
    echo "  $0 /path/to/my-secrets.env          # Use custom file"
    echo "  $0 ~/.aws/eb-secrets-production.env # Production secrets"
    exit 0
fi

# Run the main function
main "$@"
