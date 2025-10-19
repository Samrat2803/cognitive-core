#!/bin/bash

###############################################################################
# Backend Control Script - Start/Stop Elastic Beanstalk Environment
###############################################################################
# Easily shutdown and recreate your backend to save costs when not in use
###############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_NAME="political-analyst-backend-lb"
APP_NAME="political-analyst-backend"
INSTANCE_TYPE="t3.micro"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              BACKEND CONTROL PANEL                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check current status
echo -e "${YELLOW}Checking current backend status...${NC}"
STATUS=$(aws elasticbeanstalk describe-environments \
    --environment-names $ENV_NAME \
    --query 'Environments[0].Status' \
    --output text 2>/dev/null || echo "NotFound")

if [ "$STATUS" == "NotFound" ] || [ "$STATUS" == "Terminated" ]; then
    echo -e "${RED}❌ Backend is currently: TERMINATED${NC}"
    echo ""
    CURRENT_STATE="off"
else
    HEALTH=$(aws elasticbeanstalk describe-environments \
        --environment-names $ENV_NAME \
        --query 'Environments[0].Health' \
        --output text)
    echo -e "${GREEN}✅ Backend is currently: $STATUS (Health: $HEALTH)${NC}"
    echo ""
    CURRENT_STATE="on"
fi

# Show menu
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}What would you like to do?${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$CURRENT_STATE" == "on" ]; then
    echo "1. 🛑 SHUTDOWN backend (save ~\$24/month)"
    echo "2. 📊 View environment details"
    echo "3. ❌ Exit"
else
    echo "1. ▶️  START backend (~5-10 minutes)"
    echo "2. ❌ Exit"
fi

echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        if [ "$CURRENT_STATE" == "on" ]; then
            # SHUTDOWN
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}⚠️  SHUTTING DOWN BACKEND${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "This will:"
            echo "  • Terminate the Elastic Beanstalk environment"
            echo "  • Delete EC2 instance and load balancer"
            echo "  • Save ~\$24/month"
            echo "  • Keep all data (MongoDB, S3, code)"
            echo ""
            echo -e "${RED}The backend will be completely offline until you recreate it.${NC}"
            echo ""
            read -p "Are you sure? (yes/no): " confirm
            
            if [ "$confirm" == "yes" ]; then
                echo ""
                echo -e "${YELLOW}Terminating environment...${NC}"
                cd "$(dirname "$0")/../backend_v2"
                eb terminate $ENV_NAME --force
                echo ""
                echo -e "${GREEN}✅ Backend terminated successfully!${NC}"
                echo ""
                echo -e "${GREEN}💰 Savings: ~\$24/month${NC}"
                echo -e "${GREEN}📊 New monthly cost: ~\$2-5${NC}"
                echo ""
                echo "To start it again, run: ./scripts/backend-control.sh"
            else
                echo ""
                echo -e "${YELLOW}Shutdown cancelled.${NC}"
            fi
        else
            # START
            echo ""
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${YELLOW}▶️  STARTING BACKEND${NC}"
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo "This will:"
            echo "  • Create new Elastic Beanstalk environment"
            echo "  • Launch EC2 instance ($INSTANCE_TYPE) and load balancer"
            echo "  • Set all environment variables"
            echo "  • Deploy latest code"
            echo ""
            echo -e "${YELLOW}⏱️  Time: ~5-10 minutes${NC}"
            echo -e "${YELLOW}💰 Cost: ~\$29/month${NC}"
            echo ""
            read -p "Proceed? (yes/no): " confirm
            
            if [ "$confirm" == "yes" ]; then
                echo ""
                cd "$(dirname "$0")/../backend_v2"
                
                # Check if .elasticbeanstalk/config.yml exists
                if [ ! -f ".elasticbeanstalk/config.yml" ]; then
                    echo -e "${YELLOW}Initializing Elastic Beanstalk...${NC}"
                    eb init -p python-3.11 $APP_NAME --region us-east-1
                fi
                
                echo -e "${YELLOW}Creating environment...${NC}"
                eb create $ENV_NAME \
                    --instance-type $INSTANCE_TYPE \
                    --envvars BACKEND_BASE_URL=https://d1h4cjcbl77aah.cloudfront.net
                
                echo ""
                echo -e "${YELLOW}Setting additional environment variables...${NC}"
                
                # Read .env and set variables
                if [ -f ".env" ]; then
                    while IFS='=' read -r key value; do
                        # Skip comments and empty lines
                        [[ $key =~ ^#.*$ ]] && continue
                        [[ -z "$key" ]] && continue
                        
                        # Remove quotes from value
                        value=$(echo $value | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
                        
                        echo "  Setting: $key"
                        eb setenv "$key=$value" > /dev/null 2>&1 || true
                    done < .env
                fi
                
                echo ""
                echo -e "${GREEN}✅ Backend started successfully!${NC}"
                echo ""
                echo -e "${GREEN}Backend URL: https://d1h4cjcbl77aah.cloudfront.net${NC}"
                echo -e "${GREEN}Frontend URL: https://d2dk8wkh2d0mmy.cloudfront.net${NC}"
                echo ""
                echo "Testing backend health..."
                sleep 10
                curl -s https://d1h4cjcbl77aah.cloudfront.net/health | jq '.' || echo "Backend starting up..."
                
            else
                echo ""
                echo -e "${YELLOW}Start cancelled.${NC}"
            fi
        fi
        ;;
    2)
        if [ "$CURRENT_STATE" == "on" ]; then
            # VIEW DETAILS
            echo ""
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${BLUE}ENVIRONMENT DETAILS${NC}"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            aws elasticbeanstalk describe-environments \
                --environment-names $ENV_NAME \
                --query 'Environments[0].{Name:EnvironmentName,Status:Status,Health:Health,URL:CNAME,Created:DateCreated,Updated:DateUpdated}' \
                --output table
        else
            echo ""
            echo -e "${YELLOW}Exiting...${NC}"
        fi
        ;;
    3)
        echo ""
        echo -e "${YELLOW}Exiting...${NC}"
        ;;
    *)
        echo ""
        echo -e "${RED}Invalid choice.${NC}"
        ;;
esac

echo ""

