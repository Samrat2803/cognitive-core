# 🚀 Complete Deployment Guide - V2 Architecture

## Overview

This guide covers deploying both **Backend V2** (Political Analyst with LangGraph) and **Frontend V2** (Vite + Advanced UI) to AWS infrastructure.

---

## 📋 Prerequisites

### 1. AWS CLI Installation
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2. AWS EB CLI Installation
```bash
pip install awsebcli --upgrade --user
```

### 3. AWS Credentials Configuration
```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region: us-east-1
# - Default output format: json
```

### 4. Required AWS Permissions
Your AWS user needs these IAM policies:
- `AmazonS3FullAccess`
- `CloudFrontFullAccess`
- `AWSElasticBeanstalkFullAccess`
- `IAMReadOnlyAccess`

---

## 🔧 Backend V2 Deployment (Political Analyst)

### File: `backend_v2/`

**Features:**
- LangGraph Master Agent (7-node workflow)
- Real-time web search (Tavily API)
- Automatic artifact generation (charts/graphs)
- S3 integration for artifact storage
- WebSocket streaming support
- MongoDB integration (optional)

### Step 1: Create Environment File

Create `backend_v2/.env`:
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here

# Optional MongoDB
MONGODB_CONNECTION_STRING=your_mongodb_uri_here

# Optional S3 for Artifacts
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
AWS_REGION=us-east-1

# Optional CORS
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain.cloudfront.net

# LangFuse (disabled by default)
# LANGFUSE_PUBLIC_KEY=your_key
# LANGFUSE_SECRET_KEY=your_secret
```

### Step 2: Deploy to AWS Elastic Beanstalk

```bash
cd backend_v2
./aws-deploy-backend.sh
```

The script will:
- ✅ Install EB CLI if needed
- ✅ Initialize EB application
- ✅ Create production environment (t3.medium instance)
- ✅ Set environment variables from .env
- ✅ Deploy application
- ✅ Provide backend URL

### Step 3: Verify Deployment

```bash
# Check health
curl http://your-backend-url.elasticbeanstalk.com/health

# Test analyze endpoint
curl -X POST http://your-backend-url.elasticbeanstalk.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the GDP growth of India?"}'
```

### Backend V2 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root health check |
| `/health` | GET | Detailed health status |
| `/api/analyze` | POST | Political analysis with artifacts |
| `/api/artifacts/{artifact_id}.html` | GET | Get HTML artifact |
| `/api/artifacts/{artifact_id}.png` | GET | Get PNG artifact |
| `/ws/analyze` | WebSocket | Streaming analysis |

---

## 🎨 Frontend V2 Deployment (Vite UI)

### File: `Frontend_v2/`

**Features:**
- Modern Vite build system
- 80+ custom UI components
- Artifact visualization panel
- Real-time chat interface
- Citations and source linking
- Theme switching (dark/light)
- Resizable panels
- WebSocket streaming

### Step 1: Update API Configuration

Create `Frontend_v2/.env.production`:
```bash
VITE_API_URL=http://your-backend-url.elasticbeanstalk.com
VITE_WS_URL=ws://your-backend-url.elasticbeanstalk.com
```

Or update the code directly in `Frontend_v2/src/services/WebSocketService.ts` and related files.

### Step 2: Deploy to AWS S3 + CloudFront

**Option A: Secure Deployment (Recommended)**
```bash
cd Frontend_v2
./aws-deploy-secure.sh
```

**Option B: Public S3 Website**
```bash
cd Frontend_v2
./aws-deploy.sh
```

The script will:
- ✅ Build production bundle with Vite
- ✅ Create S3 bucket (private with OAC)
- ✅ Upload all files to S3
- ✅ Create CloudFront distribution
- ✅ Configure SSL/HTTPS
- ✅ Set up SPA routing (404 → index.html)
- ✅ Provide CloudFront URL

### Step 3: Update CORS on Backend

After getting your CloudFront URL, update backend CORS:

```bash
cd backend_v2
eb setenv CORS_ORIGINS="http://localhost:5173,https://your-cloudfront-domain.cloudfront.net"
eb deploy
```

### Step 4: Verify Frontend

Open `https://your-cloudfront-domain.cloudfront.net` and test:
- ✅ Page loads correctly
- ✅ Can submit analysis queries
- ✅ Artifacts display properly
- ✅ WebSocket connection works
- ✅ Citations render correctly

---

## 📊 Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Infrastructure                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   CloudFront     │         │  Elastic         │          │
│  │   (Frontend V2)  │────────▶│  Beanstalk       │          │
│  │                  │  CORS   │  (Backend V2)    │          │
│  │  React + Vite    │         │  FastAPI         │          │
│  │  80+ Components  │         │  Python 3.11     │          │
│  └──────────────────┘         └──────────────────┘          │
│          │                             │                     │
│          │                             │                     │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   S3 Bucket      │         │  LangGraph       │          │
│  │   (Static Files) │         │  Master Agent    │          │
│  │                  │         │  7-Node Workflow │          │
│  └──────────────────┘         └──────────────────┘          │
│                                         │                     │
│                                         ├─────────────────┐   │
│                                         │                 │   │
│                                ┌────────▼─────┐  ┌───────▼──┐│
│                                │ Tavily API   │  │ OpenAI   ││
│                                │ (Web Search) │  │ (LLM)    ││
│                                └──────────────┘  └──────────┘│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Update & Maintenance

### Update Backend V2
```bash
cd backend_v2

# Make your code changes...

# Deploy
eb deploy political-analyst-backend-prod

# Check logs
eb logs political-analyst-backend-prod

# Check status
eb status political-analyst-backend-prod
```

### Update Frontend V2
```bash
cd Frontend_v2

# Make your code changes...

# Build
npm run build

# Sync to S3
aws s3 sync dist/ s3://YOUR_BUCKET_NAME/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

---

## 🧪 Testing Deployed Application

### Test Backend
```bash
# Health check
curl http://your-backend.elasticbeanstalk.com/health

# Test analysis endpoint
curl -X POST http://your-backend.elasticbeanstalk.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a visualization of India'\''s GDP growth since 2020",
    "user_session": "test-session"
  }'
```

### Test Frontend
1. Open `https://your-frontend.cloudfront.net`
2. Enter query: "Analyze climate policy trends in 2024"
3. Verify:
   - ✅ Query submits successfully
   - ✅ Loading indicator appears
   - ✅ Response displays with markdown
   - ✅ Citations render correctly
   - ✅ Artifacts (charts) load in right panel
   - ✅ WebSocket connection indicator shows green

---

## 🚨 Troubleshooting

### Backend Issues

**Problem: 502 Bad Gateway**
```bash
# Check application logs
eb logs political-analyst-backend-prod --all

# Common causes:
# 1. Missing API keys in environment
# 2. Port not set to 8000
# 3. Application startup errors
```

**Problem: Module Import Errors**
```bash
# Verify requirements.txt is complete
# Re-deploy with clean environment
eb terminate political-analyst-backend-prod
./aws-deploy-backend.sh
```

**Problem: Artifacts Not Loading**
```bash
# Check S3 bucket exists
aws s3 ls s3://YOUR_BUCKET_NAME/

# Check S3 permissions
# Verify AWS credentials in environment variables
```

### Frontend Issues

**Problem: API Calls Failing**
- Check CORS settings on backend
- Verify API URL in frontend config
- Check browser console for errors

**Problem: 404 on Direct URLs**
- Verify CloudFront error pages configuration
- Ensure 403/404 redirect to index.html

**Problem: Artifacts Not Displaying**
- Check backend artifact endpoints
- Verify CORS allows artifact requests
- Check browser console for loading errors

---

## 💰 Cost Estimation

### Monthly AWS Costs (Approximate)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| Elastic Beanstalk | t3.medium instance | ~$30-40 |
| S3 Storage | ~1GB frontend files | ~$0.50 |
| CloudFront | ~100GB transfer | ~$8-10 |
| S3 Artifacts | ~10GB storage | ~$0.25 |
| **Total** | | **~$40-50/month** |

*Note: Actual costs vary based on traffic and usage*

---

## 🎯 Performance Optimization

### Backend
- ✅ Use async operations throughout
- ✅ Enable response caching for repeated queries
- ✅ Store artifacts in S3 for scalability
- ✅ Use connection pooling for MongoDB
- ✅ Set appropriate instance type (t3.medium)

### Frontend
- ✅ Vite for fast builds
- ✅ CloudFront CDN for global distribution
- ✅ Asset compression enabled
- ✅ Long cache headers on static files
- ✅ Short cache on HTML files
- ✅ Lazy loading for components

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] AWS CLI installed and configured
- [ ] EB CLI installed
- [ ] .env files created with all required keys
- [ ] MongoDB connection string ready (if using)
- [ ] S3 bucket created (if using artifacts)
- [ ] Domain name ready (optional)

### Backend V2 Deployment
- [ ] Run `./aws-deploy-backend.sh`
- [ ] Verify health endpoint
- [ ] Test analyze endpoint
- [ ] Test artifact generation
- [ ] Verify WebSocket connection
- [ ] Save backend URL

### Frontend V2 Deployment
- [ ] Update API URL in config
- [ ] Run `./aws-deploy-secure.sh`
- [ ] Wait for CloudFront distribution (15-20 min)
- [ ] Update backend CORS with frontend URL
- [ ] Test frontend application
- [ ] Verify all features work
- [ ] Save CloudFront URL

### Post-Deployment
- [ ] Document all URLs
- [ ] Set up monitoring/alerts
- [ ] Configure backup strategy
- [ ] Plan update workflow
- [ ] Share URLs with team

---

## 🎉 Success Criteria

Your deployment is successful when:

1. ✅ Backend health endpoint returns 200 OK
2. ✅ Frontend loads without errors
3. ✅ Can submit queries and get responses
4. ✅ Artifacts generate and display correctly
5. ✅ WebSocket streaming works
6. ✅ Citations render properly
7. ✅ Mobile responsive
8. ✅ HTTPS enabled
9. ✅ CORS configured correctly
10. ✅ Error handling works gracefully

---

## 📞 Support

For deployment issues:
1. Check logs: `eb logs <env-name>`
2. Verify environment variables: `eb printenv <env-name>`
3. Check CloudWatch logs in AWS Console
4. Review CloudFront distribution status
5. Test endpoints with curl/Postman

---

## 🔐 Security Best Practices

1. **Never commit .env files** to git
2. **Use AWS Secrets Manager** for production secrets
3. **Enable CloudFront WAF** for DDoS protection
4. **Use HTTPS only** (CloudFront provides SSL)
5. **Restrict S3 bucket access** (use OAC)
6. **Rotate API keys** regularly
7. **Enable CloudWatch logging**
8. **Set up billing alerts**

---

**Deployment Complete! 🎊**

Your Political Analyst Workbench V2 is now live on AWS infrastructure with:
- ✅ Scalable backend with LangGraph agents
- ✅ Modern React frontend with Vite
- ✅ Global CDN distribution
- ✅ Real-time artifact generation
- ✅ WebSocket streaming support
- ✅ Production-ready architecture

