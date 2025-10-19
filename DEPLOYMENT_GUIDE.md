# 🚀 Political Analyst Workbench - Complete Deployment Guide

**Version:** 2.0  
**Last Updated:** October 2, 2025  
**Estimated Time:** 45-60 minutes (first-time deployment)

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (TL;DR)](#quick-start-tldr)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Testing & Verification](#testing--verification)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Rollback Procedures](#rollback-procedures)
8. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Tools:
```bash
# Check if installed
aws --version        # AWS CLI
eb --version         # Elastic Beanstalk CLI
node --version       # Node.js (v18+)
npm --version        # NPM
git --version        # Git
```

### Install Missing Tools:
```bash
# AWS CLI
pip install awscli

# EB CLI
pip install awsebcli

# Node.js (if not installed)
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm
```

### AWS Credentials:
```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Verify credentials
aws sts get-caller-identity
```

### Required Secrets:
Create `.env` file in `backend_v2/` with:
```bash
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-dev-...
MONGODB_CONNECTION_STRING=mongodb+srv://...
```

**⚠️ NEVER commit `.env` to Git!**

---

## Quick Start (TL;DR)

For experienced teams who know AWS:

```bash
# 1. Backend (from backend_v2/)
eb init -p python-3.11 political-analyst-backend --region us-east-1
eb create political-analyst-backend-lb --elb-type application --instance-type t3.small
eb setenv $(cat .env | xargs)
# Create CloudFront for backend → Get domain: d1h4cjcbl77aah.cloudfront.net

# 2. Frontend (from Frontend_v2/)
# Update src/config.ts with CloudFront domain
npm install && npm run build
aws s3 sync dist/ s3://YOUR_BUCKET/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"

# 3. Test
curl https://YOUR_CLOUDFRONT_DOMAIN/health
# Visit https://YOUR_FRONTEND_CLOUDFRONT/
```

**Continue reading for detailed steps and troubleshooting.**

---

## Backend Deployment

### Step 1: Prepare Backend Files

```bash
cd /Users/YOUR_USER/Desktop/code/tavily_assignment/exp_2/backend_v2
```

**⚠️ CRITICAL: Create `.ebignore` file**

This prevents deploying unnecessary files (reduces package from 109MB → 22MB):

```bash
cat > .ebignore << 'EOF'
# Virtual environments (CRITICAL - prevents 108MB deployment)
.venv/
venv/
env/
__pycache__/

# Artifacts (stored in S3, not needed in deployment)
artifacts/

# Test and debug files
test_*.py
*_test.py
visualize_*.py
*_DEBUG_*.md
*_SUMMARY.md
*_FLOW_LOG.md

# IDE files
.vscode/
.idea/
*.swp

# Git
.git/

# Environment backup files (CRITICAL - contains secrets!)
.env.bak
.env.backup

# Logs
*.log
nohup.out
EOF
```

**Why this matters:** Without `.ebignore`, deployment will:
- ❌ Upload 109MB (slow + fails)
- ❌ Expose secrets in `.env.bak`
- ❌ Cause GitHub push protection errors

### Step 2: Create Load Balancer Config

**Why:** WebSocket requires Application Load Balancer (not single instance)

```bash
mkdir -p .ebextensions
cat > .ebextensions/01_websocket.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:environment:
    LoadBalancerType: application
EOF
```

### Step 3: Initialize Elastic Beanstalk

```bash
# Initialize EB application
eb init -p python-3.11 political-analyst-backend --region us-east-1

# Verify .elasticbeanstalk/config.yml was created
ls -la .elasticbeanstalk/
```

### Step 4: Create Load-Balanced Environment

**⏱ Time: ~5-7 minutes**

```bash
eb create political-analyst-backend-lb \
  --elb-type application \
  --instance-type t3.small \
  --min-instances 1 \
  --max-instances 2 \
  --envvars PORT=8000,ENABLE_QUERY_CACHE=false
```

**Monitor progress:**
```bash
# In another terminal
watch -n 5 'aws elasticbeanstalk describe-environments \
  --environment-names political-analyst-backend-lb \
  --query "Environments[0].{Status:Status,Health:Health}" \
  --output table'
```

**Expected output:**
```
Status: Ready
Health: Green
URL: political-analyst-backend-lb.eba-XXXXXX.us-east-1.elasticbeanstalk.com
```

### Step 5: Set Environment Variables

```bash
# Switch to new environment
eb use political-analyst-backend-lb

# Set API keys (one by one to avoid shell escaping issues)
eb setenv \
  OPENAI_API_KEY="$(grep OPENAI_API_KEY .env | cut -d '=' -f2-)" \
  TAVILY_API_KEY="$(grep TAVILY_API_KEY .env | cut -d '=' -f2-)" \
  MONGODB_CONNECTION_STRING="$(grep MONGODB_CONNECTION_STRING .env | cut -d '=' -f2-)" \
  CORS_ORIGINS="*" \
  ENABLE_QUERY_CACHE=false
```

**⏱ Time: ~1-2 minutes**

### Step 6: Verify Backend Health

```bash
# Get backend URL
BACKEND_URL=$(eb status | grep "CNAME" | awk '{print $2}')
echo "Backend URL: http://$BACKEND_URL"

# Test health endpoint
curl -s http://$BACKEND_URL/health | jq .

# Expected output:
# {
#   "status": "healthy",
#   "agent_status": "ready"
# }
```

### Step 7: Create CloudFront Distribution (SSL for WebSocket)

**Why needed:** Browser blocks `ws://` connections from HTTPS pages.  
**Solution:** CloudFront provides free SSL and supports WebSocket.

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config '{
    "CallerReference": "backend-'$(date +%s)'",
    "Comment": "Backend with WebSocket SSL",
    "Enabled": true,
    "Origins": {
      "Quantity": 1,
      "Items": [{
        "Id": "backend-lb",
        "DomainName": "'$BACKEND_URL'",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }]
    },
    "DefaultCacheBehavior": {
      "TargetOriginId": "backend-lb",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {
        "Quantity": 7,
        "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      },
      "MinTTL": 0,
      "DefaultTTL": 0,
      "MaxTTL": 0,
      "ForwardedValues": {
        "QueryString": true,
        "Cookies": {"Forward": "all"},
        "Headers": {
          "Quantity": 1,
          "Items": ["*"]
        }
      }
    },
    "ViewerCertificate": {
      "CloudFrontDefaultCertificate": true,
      "MinimumProtocolVersion": "TLSv1.2_2021"
    }
  }' \
  --output json | jq -r '{DomainName: .Distribution.DomainName, Id: .Distribution.Id, Status: .Distribution.Status}'
```

**⏱ Time: ~2-5 minutes to deploy**

**Save the output:**
```json
{
  "DomainName": "d1h4cjcbl77aah.cloudfront.net",
  "Id": "E3TIOD2VTRLS8Y",
  "Status": "InProgress"
}
```

**Monitor deployment:**
```bash
BACKEND_CF_ID="E3TIOD2VTRLS8Y"  # Replace with your ID

# Check every 30 seconds
while true; do
  STATUS=$(aws cloudfront get-distribution --id $BACKEND_CF_ID --query 'Distribution.Status' --output text)
  echo "CloudFront Status: $STATUS"
  [ "$STATUS" = "Deployed" ] && break
  sleep 30
done
```

### Step 8: Test Backend with SSL

```bash
BACKEND_CF_DOMAIN="d1h4cjcbl77aah.cloudfront.net"  # Replace with your domain

# Test HTTPS health check
curl -s https://$BACKEND_CF_DOMAIN/health | jq .

# Test graph API
curl -s https://$BACKEND_CF_DOMAIN/api/graph/structure | jq '{nodes: (.nodes | length), edges: (.edges | length)}'

# Test CORS
curl -s -H "Origin: https://YOUR_FRONTEND_DOMAIN" \
  https://$BACKEND_CF_DOMAIN/health -I | grep -i "access-control"
```

**✅ All tests should pass before proceeding to frontend.**

---

## Frontend Deployment

### Step 1: Update Configuration

Edit `Frontend_v2/src/config.ts`:

```typescript
// Application Configuration

const isProd = import.meta.env.PROD;

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || (isProd 
    ? 'https://d1h4cjcbl77aah.cloudfront.net'  // ← YOUR BACKEND CLOUDFRONT
    : 'http://localhost:8001'),
  
  wsUrl: import.meta.env.VITE_WS_URL || (isProd
    ? 'wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze'  // ← YOUR BACKEND CLOUDFRONT (wss://)
    : 'ws://localhost:8001/ws/analyze'),
};
```

**⚠️ CRITICAL:**
- Use `https://` for apiUrl
- Use `wss://` (secure WebSocket) for wsUrl
- **NOT** `ws://` or browser will block it

### Step 2: Build Frontend

```bash
cd /Users/YOUR_USER/Desktop/code/tavily_assignment/exp_2/Frontend_v2

# Install dependencies (if not done)
npm install

# Build for production
npm run build

# Verify build output
ls -lh dist/
# Should show ~500KB JS bundle
```

### Step 3: Create S3 Bucket (First Time Only)

```bash
# Create unique bucket name
BUCKET_NAME="political-analyst-frontend-$(date +%s)"
echo $BUCKET_NAME

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Enable static website hosting
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document index.html

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::'$BUCKET_NAME'/*"
  }]
}'

# Save bucket name
echo "BUCKET_NAME=$BUCKET_NAME" > deployment-info.txt
```

### Step 4: Create Frontend CloudFront Distribution

```bash
aws cloudfront create-distribution \
  --origin-domain-name $BUCKET_NAME.s3.amazonaws.com \
  --default-root-object index.html \
  --output json | jq -r '{DomainName: .Distribution.DomainName, Id: .Distribution.Id}'
```

**Save the output:**
```json
{
  "DomainName": "d2dk8wkh2d0mmy.cloudfront.net",
  "Id": "E1YO4Y7KXANJNR"
}
```

**Save to file:**
```bash
echo "CLOUDFRONT_DOMAIN=d2dk8wkh2d0mmy.cloudfront.net" >> deployment-info.txt
echo "CLOUDFRONT_ID=E1YO4Y7KXANJNR" >> deployment-info.txt
```

### Step 5: Deploy Frontend

```bash
# Read deployment info
source deployment-info.txt

# Upload to S3
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_ID \
  --paths "/*"
```

**⏱ Time: CloudFront cache invalidation takes ~1-2 minutes**

---

## Testing & Verification

### 1. Backend Tests

```bash
BACKEND_URL="https://d1h4cjcbl77aah.cloudfront.net"

# Health check
curl -s $BACKEND_URL/health | jq .
# Expected: {"status": "healthy", "agent_status": "ready"}

# Graph structure
curl -s $BACKEND_URL/api/graph/structure | jq '{nodes: (.nodes | length), edges: (.edges | length)}'
# Expected: {"nodes": 9, "edges": 10}

# CORS (should return access-control-allow-origin)
curl -s -I $BACKEND_URL/health | grep -i "access-control"
# Expected: access-control-allow-origin: *
```

### 2. Frontend Tests

**In Browser:**
1. Open `https://d2dk8wkh2d0mmy.cloudfront.net` (your CloudFront domain)
2. Open Developer Console (F12)
3. Check for errors (should be none)
4. Try a query: "What's the latest news about US politics?"
5. Verify:
   - ✅ Real-time streaming works
   - ✅ Progress updates show
   - ✅ Citations appear
   - ✅ Execution graph loads when expanded
   - ✅ No console errors

### 3. WebSocket Test

**In Browser Console:**
```javascript
// Should show wss:// (secure)
console.log(config.wsUrl)
// Expected: "wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze"

// Should NOT show any WebSocket errors
// If you see "SecurityError" or "ws://", config is wrong
```

### 4. End-to-End Test

**Run Full Flow:**
```bash
# 1. Send query
curl -X POST https://d1h4cjcbl77aah.cloudfront.net/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "latest US political news"}' | jq .

# 2. Check execution graph
SESSION_ID="<session_id_from_above>"
curl -s https://d1h4cjcbl77aah.cloudfront.net/api/graph/execution/$SESSION_ID | jq .

# Expected: Graph with executed nodes
```

---

## Common Issues & Solutions

### Issue 1: "Package too large" (109MB)

**Symptom:**
```
Upload Complete.
ERROR: The version label exceeds the maximum allowed size
```

**Cause:** `.venv/` or `artifacts/` included in deployment

**Solution:**
```bash
# Create .ebignore file (see Step 1 of Backend Deployment)
cat > .ebignore << 'EOF'
.venv/
artifacts/
__pycache__/
.env.bak
EOF

# Verify package size
eb deploy --dry-run
# Should be ~22MB, not 109MB
```

---

### Issue 2: "WebSocket SecurityError"

**Symptom (Browser Console):**
```
SecurityError: Failed to construct 'WebSocket': 
An insecure WebSocket connection may not be initiated from a page loaded over HTTPS.
```

**Cause:** Frontend using `ws://` instead of `wss://`

**Solution:**
```typescript
// Frontend_v2/src/config.ts
wsUrl: 'wss://YOUR_CLOUDFRONT.cloudfront.net/ws/analyze'
//     ^^^^ Must be wss:// (secure), not ws://

// Rebuild and redeploy
npm run build
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete
```

---

### Issue 3: "CORS blocked"

**Symptom:**
```
Access to fetch at 'https://backend...' from origin 'https://frontend...' 
has been blocked by CORS policy
```

**Solution:**
```bash
# Set CORS on backend
eb setenv CORS_ORIGINS="*"
# Or specific domain:
eb setenv CORS_ORIGINS="https://d2dk8wkh2d0mmy.cloudfront.net"
```

---

### Issue 4: "Environment already exists"

**Symptom:**
```
ERROR: InvalidParameterValueError - Environment political-analyst-backend-lb already exists.
```

**Solution:**
```bash
# Option A: Use existing environment
eb use political-analyst-backend-lb
eb deploy

# Option B: Terminate and recreate
eb terminate political-analyst-backend-lb --force
# Wait 2-3 minutes, then create again
```

---

### Issue 5: "CloudFront header error"

**Symptom:**
```
InvalidArgument: The parameter Header Name with value Connection is not allowed.
```

**Solution:**
Use wildcard header forwarding:
```json
"Headers": {
  "Quantity": 1,
  "Items": ["*"]
}
```

**NOT:**
```json
"Headers": {
  "Items": ["Connection", "Upgrade"]  // ❌ These are blocked
}
```

---

### Issue 6: "404 Not Found for execution graph"

**Symptom:**
```
GET /api/graph/execution/session_... 404 (Not Found)
```

**Cause:** Query cache enabled OR WebSocket not saving to MongoDB

**Solution:**
```bash
# Disable cache
eb setenv ENABLE_QUERY_CACHE=false

# Verify MongoDB connection
eb logs | grep -i mongodb
```

---

### Issue 7: "GitHub push rejected - secrets detected"

**Symptom:**
```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Push cannot contain secrets
```

**Cause:** `.env.bak` or secrets in commit

**Solution:**
```bash
# Remove from staging
git reset HEAD .env.bak backend_v2/.env.bak

# Delete file
rm .env.bak

# Add to .gitignore
echo ".env.bak" >> .gitignore

# Commit again
git add -A
git commit -m "fix: Remove secrets"
git push origin main
```

---

## Rollback Procedures

### Rollback Backend

```bash
# List previous versions
eb appversion

# Deploy previous version
eb deploy --version <previous-version-label>

# Or swap environments (if you have blue-green)
eb swap <current-env> <previous-env>
```

### Rollback Frontend

```bash
# S3 versioning should be enabled
aws s3api get-bucket-versioning --bucket $BUCKET_NAME

# Restore previous version (if versioning enabled)
aws s3api list-object-versions --bucket $BUCKET_NAME --prefix index.html

# Or rebuild from previous commit
git checkout <previous-commit>
cd Frontend_v2
npm run build
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete
```

---

## Cost Optimization

### Production Costs (~$38-42/month)

| Resource | Cost | Optimization |
|----------|------|--------------|
| Application Load Balancer | $16/mo | **Cannot reduce** (required for WebSocket) |
| EC2 (t3.small) | $15/mo | Switch to t3.micro ($7.50/mo) if traffic is low |
| CloudFront (Backend) | $5-10/mo | Pay per use |
| CloudFront (Frontend) | $1-5/mo | Pay per use |
| S3 | <$1/mo | Minimal |

### Cost Reduction Options:

1. **Use Spot Instances** (not recommended for production):
```bash
eb create ... --instance-type t3.small --spot-max-price 0.01
```

2. **Single Instance** (loses WebSocket SSL):
```bash
# Only for development
eb create ... --single
```

3. **Auto-scaling limits**:
```bash
eb scale 1  # Min=Max=1 instance
```

4. **Regional restrictions** (reduce CloudFront costs):
```json
"PriceClass": "PriceClass_100"  // US, Canada, Europe only
```

---

## Monitoring & Logs

### View Logs

```bash
# Backend logs (last 100 lines)
eb logs --all

# Tail live logs
eb ssh
tail -f /var/log/web.stdout.log

# CloudWatch logs
aws logs tail /aws/elasticbeanstalk/political-analyst-backend-lb/var/log/web.stdout.log --follow
```

### Health Monitoring

```bash
# Environment health
eb health

# Detailed health
eb health --refresh

# CloudWatch dashboard
aws cloudwatch get-dashboard --dashboard-name political-analyst
```

---

## Maintenance

### Update Backend Code

```bash
cd backend_v2

# Pull latest changes
git pull origin main

# Deploy
eb deploy political-analyst-backend-lb

# Monitor deployment
eb health --refresh
```

### Update Frontend

```bash
cd Frontend_v2

# Pull latest changes
git pull origin main

# Build
npm run build

# Deploy
aws s3 sync dist/ s3://$BUCKET_NAME/ --delete
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
```

### Update Environment Variables

```bash
# Add/update a variable
eb setenv NEW_VAR="value"

# Update from .env file
while IFS='=' read -r key value; do
  [[ $key =~ ^#.*$ ]] && continue
  [[ -z $key ]] && continue
  eb setenv "$key=$value"
done < .env
```

---

## Cleanup (Terminate Everything)

**⚠️ WARNING: This will delete all resources**

```bash
# Backend
eb terminate political-analyst-backend-lb --force

# Frontend S3
aws s3 rb s3://$BUCKET_NAME --force

# Frontend CloudFront
aws cloudfront delete-distribution --id $CLOUDFRONT_ID --if-match <ETag>

# Backend CloudFront
aws cloudfront delete-distribution --id $BACKEND_CF_ID --if-match <ETag>
```

---

## Quick Reference

### Essential URLs

```bash
# Production
FRONTEND_URL="https://d2dk8wkh2d0mmy.cloudfront.net"
BACKEND_URL="https://d1h4cjcbl77aah.cloudfront.net"
WEBSOCKET_URL="wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze"

# Development
FRONTEND_URL="http://localhost:3001"
BACKEND_URL="http://localhost:8001"
WEBSOCKET_URL="ws://localhost:8001/ws/analyze"
```

### Essential Commands

```bash
# Backend
eb status                 # Check status
eb health                 # Check health
eb logs                   # View logs
eb deploy                 # Deploy update
eb terminate --force      # Delete environment

# Frontend
npm run build             # Build
aws s3 sync dist/ s3://... # Upload
aws cloudfront create-invalidation ... # Clear cache

# Testing
curl https://.../health   # Backend health
curl https://.../api/graph/structure  # Graph API
```

---

## Support

### Documentation
- `WEBSOCKET_SSL_COMPLETE.md` - WebSocket setup details
- `DEPLOYMENT_SUMMARY.md` - Current deployment status
- `README.md` - Project overview

### AWS Resources
- [Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [CloudFront Docs](https://docs.aws.amazon.com/cloudfront/)
- [WebSocket on CloudFront](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-working-with.websockets.html)

### Troubleshooting
- Check `eb logs` for backend errors
- Check browser console for frontend errors
- Check CloudWatch for system metrics
- Check S3 bucket for deployed files

---

## Deployment Checklist

Before marking deployment as complete, verify:

- [ ] Backend health check returns `{"status": "healthy"}`
- [ ] Graph API returns 9 nodes and 10 edges
- [ ] CORS headers present (`access-control-allow-origin`)
- [ ] Frontend loads without console errors
- [ ] WebSocket connects (check `wss://` in console)
- [ ] Real-time streaming works
- [ ] Execution graph displays and is interactive
- [ ] Citations appear correctly
- [ ] Artifacts generate and display
- [ ] All environment variables set
- [ ] `.env` file NOT committed to Git
- [ ] CloudFront distributions show "Deployed" status
- [ ] Cost monitoring alerts configured (optional)

---

**🎉 Deployment Complete!**

Your Political Analyst Workbench is now live and fully functional with:
- ✅ HTTPS/WSS secure connections
- ✅ Real-time WebSocket streaming
- ✅ Interactive execution graphs
- ✅ Load-balanced backend
- ✅ Auto-scaling capabilities

**Total Deployment Time:** 45-60 minutes (first time)  
**Subsequent Deployments:** 10-15 minutes

---

**Questions or Issues?**  
Review the [Common Issues & Solutions](#common-issues--solutions) section or check `eb logs` for detailed error messages.

