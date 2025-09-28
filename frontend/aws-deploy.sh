#!/bin/bash
# AWS S3 + CloudFront Deployment Script for Team C Frontend

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUCKET_NAME="tavily-research-frontend-$(date +%s)"
REGION="us-east-1"
PROFILE="default"

echo -e "${BLUE}🚀 Starting AWS S3 + CloudFront Deployment${NC}"
echo -e "${BLUE}=================================================${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    echo "Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity --profile $PROFILE &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured.${NC}"
    echo "Configure with: aws configure --profile $PROFILE"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI and credentials verified${NC}"

# Build the React app
echo -e "${BLUE}📦 Building React application...${NC}"
npm run build

if [ ! -d "build" ]; then
    echo -e "${RED}❌ Build directory not found. Build failed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ React app built successfully${NC}"

# Create S3 bucket
echo -e "${BLUE}🪣 Creating S3 bucket: $BUCKET_NAME${NC}"
aws s3 mb s3://$BUCKET_NAME --region $REGION --profile $PROFILE

# Configure bucket for static website hosting
echo -e "${BLUE}🌐 Configuring S3 static website hosting...${NC}"
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html \
    --profile $PROFILE

# Set bucket policy for public read access
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file://bucket-policy.json \
    --profile $PROFILE

echo -e "${GREEN}✅ S3 bucket configured${NC}"

# Upload build files to S3
echo -e "${BLUE}📤 Uploading files to S3...${NC}"
aws s3 sync build/ s3://$BUCKET_NAME/ \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html" \
    --profile $PROFILE

# Upload HTML files with no cache
aws s3 sync build/ s3://$BUCKET_NAME/ \
    --delete \
    --cache-control "public, max-age=0, no-cache, no-store, must-revalidate" \
    --include "*.html" \
    --profile $PROFILE

echo -e "${GREEN}✅ Files uploaded to S3${NC}"

# Create CloudFront distribution
echo -e "${BLUE}☁️ Creating CloudFront distribution...${NC}"
cat > cloudfront-config.json << EOF
{
    "CallerReference": "tavily-frontend-$(date +%s)",
    "DefaultRootObject": "index.html",
    "Comment": "Tavily Research Agent Frontend Distribution",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "MinTTL": 0,
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        }
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "PriceClass": "PriceClass_All"
}
EOF

DISTRIBUTION_ID=$(aws cloudfront create-distribution \
    --distribution-config file://cloudfront-config.json \
    --profile $PROFILE \
    --query 'Distribution.Id' \
    --output text)

DISTRIBUTION_DOMAIN=$(aws cloudfront get-distribution \
    --id $DISTRIBUTION_ID \
    --profile $PROFILE \
    --query 'Distribution.DomainName' \
    --output text)

echo -e "${GREEN}✅ CloudFront distribution created${NC}"

# Wait for distribution to be deployed (this can take 15-20 minutes)
echo -e "${YELLOW}⏳ Waiting for CloudFront distribution to deploy (this may take 15-20 minutes)...${NC}"
echo -e "${BLUE}You can continue with other work. Check status with:${NC}"
echo -e "${BLUE}aws cloudfront get-distribution --id $DISTRIBUTION_ID --profile $PROFILE${NC}"

# Clean up temporary files
rm -f bucket-policy.json cloudfront-config.json

# Output deployment information
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "${BLUE}S3 Bucket:${NC} $BUCKET_NAME"
echo -e "${BLUE}S3 Website URL:${NC} http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo -e "${BLUE}CloudFront Distribution ID:${NC} $DISTRIBUTION_ID"
echo -e "${BLUE}CloudFront URL:${NC} https://$DISTRIBUTION_DOMAIN"
echo ""
echo -e "${YELLOW}📝 Save these details for your Team C documentation!${NC}"
echo ""
echo -e "${BLUE}To update the frontend:${NC}"
echo "1. npm run build"
echo "2. aws s3 sync build/ s3://$BUCKET_NAME/ --delete --profile $PROFILE"
echo "3. aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths '/*' --profile $PROFILE"
echo ""
echo -e "${GREEN}Frontend is now live at: https://$DISTRIBUTION_DOMAIN${NC}"
