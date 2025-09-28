#!/bin/bash
# Secure AWS S3 + CloudFront Deployment Script for Team C Frontend
# Uses CloudFront Origin Access Control instead of public bucket policies

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

echo -e "${BLUE}🚀 Starting Secure AWS S3 + CloudFront Deployment${NC}"
echo -e "${BLUE}====================================================${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
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

# Create S3 bucket (private by default)
echo -e "${BLUE}🪣 Creating private S3 bucket: $BUCKET_NAME${NC}"
aws s3 mb s3://$BUCKET_NAME --region $REGION --profile $PROFILE

echo -e "${GREEN}✅ S3 bucket created (private by default)${NC}"

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

# Create Origin Access Control for CloudFront
echo -e "${BLUE}🔐 Creating CloudFront Origin Access Control...${NC}"
OAC_ID=$(aws cloudfront create-origin-access-control \
    --origin-access-control-config '{
        "Name": "tavily-frontend-oac-'$(date +%s)'",
        "Description": "Origin Access Control for Tavily Research Frontend",
        "SigningProtocol": "sigv4",
        "SigningBehavior": "always",
        "OriginAccessControlOriginType": "s3"
    }' \
    --profile $PROFILE \
    --query 'OriginAccessControl.Id' \
    --output text)

echo -e "${GREEN}✅ Origin Access Control created: $OAC_ID${NC}"

# Create CloudFront distribution with Origin Access Control
echo -e "${BLUE}☁️ Creating secure CloudFront distribution...${NC}"
cat > cloudfront-config.json << EOF
{
    "CallerReference": "tavily-frontend-secure-$(date +%s)",
    "DefaultRootObject": "index.html",
    "Comment": "Tavily Research Agent Frontend Distribution (Secure)",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3.$REGION.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                },
                "OriginAccessControlId": "$OAC_ID"
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "Compress": true,
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        }
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            },
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "PriceClass": "PriceClass_100"
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

echo -e "${GREEN}✅ CloudFront distribution created: $DISTRIBUTION_ID${NC}"

# Update S3 bucket policy to allow CloudFront Origin Access Control
echo -e "${BLUE}🔐 Updating S3 bucket policy for CloudFront access...${NC}"
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::832721970971:distribution/$DISTRIBUTION_ID"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file://bucket-policy.json \
    --profile $PROFILE

echo -e "${GREEN}✅ S3 bucket policy updated${NC}"

# Clean up temporary files
rm -f bucket-policy.json cloudfront-config.json

echo -e "${YELLOW}⏳ CloudFront distribution is deploying (15-20 minutes)...${NC}"

# Output deployment information
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}🎉 SECURE DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "${BLUE}S3 Bucket:${NC} $BUCKET_NAME"
echo -e "${BLUE}CloudFront Distribution ID:${NC} $DISTRIBUTION_ID"
echo -e "${BLUE}CloudFront URL:${NC} https://$DISTRIBUTION_DOMAIN"
echo ""
echo -e "${BLUE}📋 Deployment Details:${NC}"
echo "- S3 Bucket: Private (secure)"
echo "- CloudFront: Origin Access Control enabled"  
echo "- SSL/HTTPS: Automatically enabled"
echo "- Caching: Optimized for performance"
echo "- SPA Support: 404/403 errors redirect to index.html"
echo ""
echo -e "${YELLOW}📝 Save these details for Team C documentation!${NC}"
echo ""
echo -e "${BLUE}To update the frontend:${NC}"
echo "1. npm run build"
echo "2. aws s3 sync build/ s3://$BUCKET_NAME/ --delete --profile $PROFILE"
echo "3. aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths '/*' --profile $PROFILE"
echo ""
echo -e "${GREEN}🚀 Frontend will be live at: https://$DISTRIBUTION_DOMAIN${NC}"
echo -e "${YELLOW}⏰ Allow 15-20 minutes for global distribution deployment${NC}"

# Save deployment info to file
cat > deployment-info.txt << EOF
# Tavily Research Frontend Deployment Information
# Generated: $(date)

S3_BUCKET_NAME=$BUCKET_NAME
CLOUDFRONT_DISTRIBUTION_ID=$DISTRIBUTION_ID  
CLOUDFRONT_DOMAIN=$DISTRIBUTION_DOMAIN
FRONTEND_URL=https://$DISTRIBUTION_DOMAIN

# Update commands:
# aws s3 sync build/ s3://$BUCKET_NAME/ --delete
# aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
EOF

echo -e "${BLUE}💾 Deployment info saved to deployment-info.txt${NC}"
