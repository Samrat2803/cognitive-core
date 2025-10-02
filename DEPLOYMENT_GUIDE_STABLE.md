# 🚀 Stable Deployment Guide - Political Analyst Workbench

**Last Updated:** October 2, 2025  
**Status:** ✅ Production Ready

---

## 📍 Stable Production URLs

These URLs **NEVER change** - safe to share with clients:

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | `https://d2dk8wkh2d0mmy.cloudfront.net` | Main application UI |
| **Backend** | `https://d1h4cjcbl77aah.cloudfront.net` | API endpoints |

---

## 🎯 One-Command Deployment

### Quick Start

```bash
# Deploy both frontend and backend
./deploy.sh

# Deploy backend only
./deploy.sh backend

# Deploy frontend only
./deploy.sh frontend

# Show help
./deploy.sh --help
```

---

## 📋 Prerequisites (One-Time Setup)

### 1. Install Required Tools

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Elastic Beanstalk CLI
pip install awsebcli

# Node.js 18+ (if not installed)
# Download from: https://nodejs.org/
```

### 2. Configure AWS Credentials

```bash
aws configure
# AWS Access Key ID: [Your Key]
# AWS Secret Access Key: [Your Secret]
# Default region: us-east-1
# Default output format: json
```

### 3. Verify Setup

```bash
# Check AWS CLI
aws --version

# Check EB CLI
eb --version

# Check Node.js
node --version

# Check deployment script
./deploy.sh --help
```

---

## 🔧 Configuration Files

### Backend Configuration

**File:** `backend_v2/.env`

```bash
# API Keys
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-...
MONGODB_CONNECTION_STRING=mongodb+srv://...

# CORS (allows frontend to call backend)
CORS_ORIGINS=https://d2dk8wkh2d0mmy.cloudfront.net

# Optional
ENABLE_QUERY_CACHE=false
LANGSMITH_API_KEY=...
```

**Important:** Never commit `.env` to Git!

### Frontend Configuration

**File:** `Frontend_v2/src/config.ts`

```typescript
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || (isProd 
    ? 'https://d1h4cjcbl77aah.cloudfront.net'  // ← NEVER CHANGE
    : 'http://localhost:8000'),
  
  wsUrl: import.meta.env.VITE_WS_URL || (isProd
    ? 'wss://d1h4cjcbl77aah.cloudfront.net/ws/analyze'  // ← NEVER CHANGE
    : 'ws://localhost:8000/ws/analyze'),
};
```

**Critical:** These URLs must remain stable!

---

## 🚀 Deployment Process

### Full Deployment (Both)

```bash
# 1. Make your code changes
git add .
git commit -m "Your changes"
git push origin main

# 2. Run deployment script
./deploy.sh

# 3. Wait for completion (~5 minutes)
#    - Backend: 2 minutes
#    - Frontend: 1 minute (build + upload)
#    - CloudFront: 2-3 minutes (cache propagation)

# 4. Test the deployment
curl https://d1h4cjcbl77aah.cloudfront.net/health
open https://d2dk8wkh2d0mmy.cloudfront.net
```

### Backend Only

```bash
# When you change Python code
./deploy.sh backend

# What happens:
# 1. Checks EB environment
# 2. Deploys to Elastic Beanstalk
# 3. Tests health endpoint
# 4. Shows status
```

### Frontend Only

```bash
# When you change React/TypeScript code
./deploy.sh frontend

# What happens:
# 1. Verifies backend URL in config
# 2. Builds production bundle
# 3. Uploads to S3
# 4. Invalidates CloudFront cache
# 5. Tests frontend URL
```

---

## ✅ Post-Deployment Checklist

### Immediate (0-5 minutes)

- [ ] Deployment script completed without errors
- [ ] Backend health check passed
- [ ] Frontend URL returns 200 OK

### After Cache Propagation (5-10 minutes)

- [ ] Open frontend URL in browser
- [ ] Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
- [ ] Live Monitor auto-fetches topics
- [ ] No console errors
- [ ] Images load correctly
- [ ] WebSocket connects (check console)

---

## 🐛 Troubleshooting

### Issue: "Backend health check failed"

**Cause:** Backend still starting up  
**Solution:** Wait 30 seconds and test again:

```bash
curl https://d1h4cjcbl77aah.cloudfront.net/health
```

### Issue: "Frontend shows old version"

**Cause:** Browser cache or CloudFront propagation  
**Solution:**

```bash
# 1. Hard refresh browser (Ctrl+Shift+R)
# 2. Clear browser cache
# 3. Wait 2-3 minutes for CloudFront
# 4. Try incognito/private mode
```

### Issue: "JSON parse error in console"

**Cause:** Frontend calling wrong API URL  
**Solution:** Verify `config.ts`:

```bash
grep "d1h4cjcbl77aah" Frontend_v2/src/config.ts
# Should show: https://d1h4cjcbl77aah.cloudfront.net
```

### Issue: "CORS error"

**Cause:** Backend CORS not configured  
**Solution:** Check backend environment variables:

```bash
cd backend_v2
eb printenv | grep CORS_ORIGINS
# Should show: https://d2dk8wkh2d0mmy.cloudfront.net
```

---

## 📊 Infrastructure Overview

```
┌─────────────────────────────────────────────────────────┐
│  Clients (Browser)                                      │
└───────────┬─────────────────────────────────────────────┘
            │
            ├─── Frontend (HTTPS)
            │    https://d2dk8wkh2d0mmy.cloudfront.net
            │    │
            │    ├─── CloudFront Distribution (E1YO4Y7KXANJNR)
            │    │    └─── S3 Bucket (tavily-research-frontend-1759377613)
            │    │         └─── React build (dist/)
            │
            └─── Backend (HTTPS)
                 https://d1h4cjcbl77aah.cloudfront.net
                 │
                 ├─── CloudFront Distribution
                 │    └─── Application Load Balancer
                 │         └─── EC2 Instance (t3.small)
                 │              └─── FastAPI + LangGraph
                 │                   ├─── MongoDB Atlas
                 │                   ├─── S3 (artifacts)
                 │                   ├─── OpenAI API
                 │                   └─── Tavily API
```

---

## 🔐 Security Best Practices

### Environment Variables

```bash
# NEVER commit these:
.env
.env.bak
.env.local
.env.production

# Use EB environment variables instead:
cd backend_v2
eb setenv OPENAI_API_KEY=sk-... TAVILY_API_KEY=tvly-...
```

### Git Ignore

Ensure `.gitignore` includes:

```
.env
.env.*
*.pem
*.key
deployment-info.txt
artifacts/
examples/
```

---

## 📈 Performance Optimization

### Frontend Bundle Size

Current: **1.3 MB** (compressed: 439 KB)

To optimize:

```bash
# Analyze bundle
cd Frontend_v2
npx vite-bundle-visualizer

# Consider code splitting for future
```

### Backend Response Times

- **Fresh request:** 20-25 seconds (LLM + API calls)
- **Cached request:** <1 second (MongoDB)
- **Cache hit rate:** ~80% after warmup

### CloudFront Caching

- **Static files (frontend):** 1 year
- **API responses:** No cache (dynamic)
- **Invalidation time:** 2-3 minutes

---

## 💰 Cost Breakdown

| Component | Monthly Cost |
|-----------|--------------|
| EC2 (t3.small) | ~$15 |
| Application Load Balancer | ~$16 |
| CloudFront (2 distributions) | ~$5-15 |
| S3 Storage | <$1 |
| MongoDB Atlas (M0) | Free |
| **Total** | **~$38-50/month** |

---

## 🔄 Rollback Procedure

### Backend Rollback

```bash
cd backend_v2

# List previous versions
eb appversion

# Deploy previous version
eb deploy --version app-251002_164645711361
```

### Frontend Rollback

```bash
cd Frontend_v2

# Checkout previous commit
git log --oneline -10  # Find commit hash
git checkout <commit-hash> -- src/

# Rebuild and deploy
npm run build
aws s3 sync dist/ s3://tavily-research-frontend-1759377613/ --delete
aws cloudfront create-invalidation --distribution-id E1YO4Y7KXANJNR --paths "/*"
```

---

## 📞 Support & Maintenance

### Regular Maintenance

**Weekly:**
- Check CloudWatch logs for errors
- Monitor MongoDB performance
- Review API usage (OpenAI, Tavily)

**Monthly:**
- Review AWS costs
- Update dependencies (npm audit, pip list --outdated)
- Test all features end-to-end

### Monitoring Commands

```bash
# Backend logs
cd backend_v2
eb logs

# Backend health
eb health

# CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElasticBeanstalk \
  --metric-name CPUUtilization \
  --dimensions Name=EnvironmentName,Value=political-analyst-backend-lb \
  --start-time 2025-10-02T00:00:00Z \
  --end-time 2025-10-02T23:59:59Z \
  --period 3600 \
  --statistics Average
```

---

## 📚 Additional Resources

### Documentation

- **Start Here:** [START_HERE_DEPLOYMENT.md](START_HERE_DEPLOYMENT.md)
- **Frontend Integration:** [FRONTEND_INTEGRATION_INSTRUCTIONS.md](FRONTEND_INTEGRATION_INSTRUCTIONS.md)
- **WebSocket SSL:** [WEBSOCKET_SSL_COMPLETE.md](WEBSOCKET_SSL_COMPLETE.md)

### AWS Resources

- [Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [CloudFront Docs](https://docs.aws.amazon.com/cloudfront/)
- [S3 Docs](https://docs.aws.amazon.com/s3/)

---

## 🎉 Success Criteria

Deployment is successful when:

✅ Backend `/health` returns `{"status": "healthy"}`  
✅ Frontend loads without errors  
✅ Live Monitor auto-fetches topics  
✅ WebSocket connects successfully  
✅ No CORS errors in console  
✅ Images load from Tavily  
✅ Caching works (<1s for cached requests)  
✅ All tests pass

---

**Client URL to Share:**  
🌐 **https://d2dk8wkh2d0mmy.cloudfront.net**

This URL will **never change** - safe to bookmark and share! 🎯

