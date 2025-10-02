#!/bin/bash
# AWS Elastic Beanstalk Deployment Script for Backend (Database & Research)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="tavily-research-backend"
ENV_NAME="tavily-research-backend-prod"
REGION="us-east-1"
PLATFORM="python-3.11"

echo -e "${BLUE}🚀 Starting AWS Elastic Beanstalk Deployment - Backend${NC}"
echo -e "${BLUE}======================================================${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo -e "${YELLOW}⚠️  EB CLI not found. Installing...${NC}"
    pip install awsebcli --upgrade --user
fi

echo -e "${GREEN}✅ AWS CLI and EB CLI verified${NC}"

# Check if required environment files exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from env.example...${NC}"
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${RED}❌ Please update .env with your actual API keys before deploying!${NC}"
        exit 1
    else
        echo -e "${RED}❌ env.example not found. Cannot create .env${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment files verified${NC}"

# Initialize EB application if not already initialized
if [ ! -d ".elasticbeanstalk" ]; then
    echo -e "${BLUE}🔧 Initializing Elastic Beanstalk application...${NC}"
    eb init -p $PLATFORM $APP_NAME --region $REGION
else
    echo -e "${GREEN}✅ Elastic Beanstalk already initialized${NC}"
fi

# Check if environment exists
if ! eb list | grep -q $ENV_NAME; then
    echo -e "${BLUE}🌍 Creating Elastic Beanstalk environment: $ENV_NAME${NC}"
    eb create $ENV_NAME --instance-type t3.small --region $REGION
else
    echo -e "${GREEN}✅ Environment $ENV_NAME already exists${NC}"
fi

# Set environment variables from .env file
echo -e "${BLUE}🔐 Setting environment variables...${NC}"
if [ -f ".env" ]; then
    # Read .env and set variables (skipping comments and empty lines)
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        # Remove quotes from value if present
        value=$(echo $value | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
        
        echo "Setting $key..."
        eb setenv "$key=$value" --environment $ENV_NAME
    done < .env
    
    echo -e "${GREEN}✅ Environment variables set${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found. Skipping environment variable setup.${NC}"
fi

# Deploy the application
echo -e "${BLUE}📦 Deploying application to Elastic Beanstalk...${NC}"
eb deploy $ENV_NAME

# Get the application URL
APP_URL=$(eb status $ENV_NAME | grep "CNAME" | awk '{print $2}')

# Output deployment information
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}🎉 BACKEND DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "${BLUE}Application Name:${NC} $APP_NAME"
echo -e "${BLUE}Environment Name:${NC} $ENV_NAME"
echo -e "${BLUE}Backend URL:${NC} http://$APP_URL"
echo -e "${BLUE}Health Check:${NC} http://$APP_URL/health"
echo ""
echo -e "${YELLOW}📝 Save these details for integration!${NC}"
echo ""
echo -e "${BLUE}To check logs:${NC}"
echo "eb logs $ENV_NAME"
echo ""
echo -e "${BLUE}To check status:${NC}"
echo "eb status $ENV_NAME"
echo ""
echo -e "${BLUE}To update:${NC}"
echo "eb deploy $ENV_NAME"
echo ""
echo -e "${GREEN}Backend is now live at: http://$APP_URL${NC}"

# Save deployment info
cat > backend-deployment-info.txt << EOF
# Backend Deployment Information
# Generated: $(date)

APP_NAME=$APP_NAME
ENV_NAME=$ENV_NAME
BACKEND_URL=http://$APP_URL
HEALTH_CHECK_URL=http://$APP_URL/health

# Management commands:
# eb logs $ENV_NAME
# eb status $ENV_NAME
# eb deploy $ENV_NAME
# eb terminate $ENV_NAME
EOF

echo -e "${BLUE}💾 Deployment info saved to backend-deployment-info.txt${NC}"

