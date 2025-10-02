# ⚡ Quick Deploy Reference - V2

## 🚀 Deploy Backend V2 in 3 Steps

```bash
# Step 1: Go to backend_v2
cd backend_v2

# Step 2: Create .env with your keys
cat > .env << EOF
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
MONGODB_CONNECTION_STRING=your_mongodb_uri
CORS_ORIGINS=http://localhost:5173
EOF

# Step 3: Deploy!
./aws-deploy-backend.sh
```

**Backend will be at**: `http://political-analyst-backend-prod.[region].elasticbeanstalk.com`

---

## 🎨 Deploy Frontend V2 in 2 Steps

```bash
# Step 1: Go to Frontend_v2
cd Frontend_v2

# Step 2: Deploy!
./aws-deploy-secure.sh
```

**Frontend will be at**: `https://[distribution-id].cloudfront.net` (wait 15-20 min)

---

## 🔄 Update Backend CORS

After frontend deploys, update backend:

```bash
cd backend_v2
eb setenv CORS_ORIGINS="https://your-frontend-domain.cloudfront.net"
eb deploy
```

---

## 📍 Key Files Created

| File | Location | Purpose |
|------|----------|---------|
| `aws-deploy-backend.sh` | `backend/` | Deploy backend v1 |
| `aws-deploy-backend.sh` | `backend_v2/` | Deploy backend v2 |
| `aws-deploy.sh` | `Frontend_v2/` | Deploy frontend (public) |
| `aws-deploy-secure.sh` | `Frontend_v2/` | Deploy frontend (secure) |
| `DEPLOYMENT_GUIDE_V2.md` | Root | Full guide |
| `DEPLOYMENT_SETUP_SUMMARY.md` | Root | What was done |

---

## ✅ What Changed

### Backend V2 (`backend_v2/`)
- ✅ Created deployment script
- ✅ Updated `requirements.txt` (removed langfuse, removed versions, added boto3)
- ✅ Existing `Procfile` and `application.py` verified

### Frontend V2 (`Frontend_v2/`)
- ✅ Copied deployment scripts from v1
- ✅ Updated for Vite (`build/` → `dist/`)
- ✅ Copied deployment documentation

---

## 🔧 Quick Commands

### Check Backend Status
```bash
cd backend_v2
eb status
eb logs
```

### Update Backend
```bash
cd backend_v2
eb deploy
```

### Update Frontend
```bash
cd Frontend_v2
npm run build
aws s3 sync dist/ s3://YOUR_BUCKET/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

---

## 🧪 Test Endpoints

### Backend V2
```bash
# Health check
curl http://your-backend.elasticbeanstalk.com/health

# Analyze
curl -X POST http://your-backend.elasticbeanstalk.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "GDP growth India 2020-2024"}'
```

### Frontend V2
Open in browser: `https://your-frontend.cloudfront.net`

---

## 💡 Pro Tips

1. **Backend First**: Always deploy backend before frontend
2. **CORS Update**: Don't forget to update CORS after frontend deploys
3. **CloudFront Wait**: CloudFront takes 15-20 minutes to propagate
4. **Save URLs**: Document both backend and frontend URLs
5. **Test Locally**: Always test with `npm run dev` / `python app.py` first

---

**That's it! You're ready to deploy! 🎉**

