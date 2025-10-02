#!/bin/bash
# AWS Elastic Beanstalk Deployment Script for Backend V2 (Political Analyst)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="political-analyst-backend"
ENV_NAME="political-analyst-backend-prod"
REGION="us-east-1"
PLATFORM="python-3.11"

echo -e "${BLUE}🚀 Starting AWS Elastic Beanstalk Deployment - Backend V2${NC}"
echo -e "${BLUE}==========================================================${NC}"

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
    echo -e "${YELLOW}⚠️  .env file not found. Please create .env with required API keys${NC}"
    echo -e "${BLUE}Required variables:${NC}"
    echo "  - OPENAI_API_KEY"
    echo "  - TAVILY_API_KEY"
    echo "  - MONGODB_CONNECTION_STRING (optional)"
    echo "  - AWS_ACCESS_KEY_ID (for S3 artifacts)"
    echo "  - AWS_SECRET_ACCESS_KEY (for S3 artifacts)"
    echo "  - S3_BUCKET_NAME (for artifacts)"
    exit 1
fi

echo -e "${GREEN}✅ Environment files verified${NC}"

# Create artifacts directory if it doesn't exist
if [ ! -d "artifacts" ]; then
    echo -e "${BLUE}📁 Creating artifacts directory...${NC}"
    mkdir -p artifacts
fi

echo -e "${GREEN}✅ Artifacts directory ready${NC}"

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
    eb create $ENV_NAME --instance-type t3.medium --region $REGION
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
echo -e "${GREEN}🎉 BACKEND V2 DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "${BLUE}Application Name:${NC} $APP_NAME"
echo -e "${BLUE}Environment Name:${NC} $ENV_NAME"
echo -e "${BLUE}Backend URL:${NC} http://$APP_URL"
echo -e "${BLUE}Health Check:${NC} http://$APP_URL/health"
echo -e "${BLUE}API Endpoint:${NC} http://$APP_URL/api/analyze"
echo ""
echo -e "${BLUE}Features Available:${NC}"
echo "  ✅ Political analysis with LangGraph Master Agent"
echo "  ✅ Real-time web search via Tavily"
echo "  ✅ Automatic artifact generation (charts/graphs)"
echo "  ✅ WebSocket support for streaming"
echo "  ✅ S3 integration for artifact storage"
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
echo -e "${GREEN}Backend V2 is now live at: http://$APP_URL${NC}"

# Save deployment info
cat > backend-deployment-info.txt << EOF
# Backend V2 Deployment Information
# Generated: $(date)

APP_NAME=$APP_NAME
ENV_NAME=$ENV_NAME
BACKEND_URL=http://$APP_URL
HEALTH_CHECK_URL=http://$APP_URL/health
ANALYZE_ENDPOINT=http://$APP_URL/api/analyze
WEBSOCKET_URL=ws://$APP_URL/ws/analyze

# Features:
# - LangGraph Master Agent Architecture
# - Real-time web search (Tavily API)
# - Artifact generation (charts, graphs)
# - WebSocket streaming support
# - S3 artifact storage

# Management commands:
# eb logs $ENV_NAME
# eb status $ENV_NAME
# eb deploy $ENV_NAME
# eb terminate $ENV_NAME
EOF

echo -e "${BLUE}💾 Deployment info saved to backend-deployment-info.txt${NC}"

