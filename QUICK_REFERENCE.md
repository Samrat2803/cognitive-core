# 🚀 Quick Reference - Political Analyst Workbench

## 📍 **Client URL (Share This)**
```
https://d2dk8wkh2d0mmy.cloudfront.net
```
**This URL never changes - safe to bookmark and share!**

---

## ⚡ **Quick Commands**

### Deploy Everything
```bash
./deploy.sh
```

### Deploy Backend Only
```bash
./deploy.sh backend
```

### Deploy Frontend Only
```bash
./deploy.sh frontend
```

### Show Help
```bash
./deploy.sh --help
```

---

## 🔧 **Configuration Files**

### Backend Environment Variables
```bash
cd backend_v2
eb printenv                    # View all
eb setenv KEY=value            # Set variable
```

### Frontend Config
```typescript
// Frontend_v2/src/config.ts
apiUrl: 'https://d1h4cjcbl77aah.cloudfront.net'  // ← NEVER CHANGE
```

---

## 🧪 **Testing**

### Test Backend
```bash
curl https://d1h4cjcbl77aah.cloudfront.net/health
```

### Test Live Monitor
```bash
curl -X POST https://d1h4cjcbl77aah.cloudfront.net/api/live-monitor/explosive-topics \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["test"], "max_results": 2}'
```

### Test Frontend
```bash
curl -I https://d2dk8wkh2d0mmy.cloudfront.net
```

---

## 🐛 **Quick Fixes**

### Frontend shows old version
```bash
# Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
# Or: Open in incognito mode
```

### Backend not responding
```bash
cd backend_v2
eb health                      # Check status
eb logs                        # View logs
```

### Clear CloudFront cache manually
```bash
aws cloudfront create-invalidation \
  --distribution-id E1YO4Y7KXANJNR \
  --paths "/*"
```

---

## 📊 **Monitoring**

### Backend Logs
```bash
cd backend_v2
eb logs                        # Latest logs
eb logs --all                  # All logs
```

### Backend Health
```bash
cd backend_v2
eb health --refresh            # Real-time health
```

### CloudWatch
```bash
# Open AWS Console → CloudWatch → Log Groups
# Look for: /aws/elasticbeanstalk/political-analyst-backend-lb
```

---

## 🔄 **Rollback**

### Backend
```bash
cd backend_v2
eb appversion                  # List versions
eb deploy --version <VERSION>  # Deploy specific version
```

### Frontend
```bash
git checkout <COMMIT> -- Frontend_v2/src/
./deploy.sh frontend
```

---

## 💰 **Cost Estimate**
~$38-50/month (EC2 + ALB + CloudFront + S3)

---

## 📚 **Documentation**
- Full Guide: `DEPLOYMENT_GUIDE_STABLE.md`
- Integration: `FRONTEND_INTEGRATION_INSTRUCTIONS.md`
- WebSocket: `WEBSOCKET_SSL_COMPLETE.md`

---

## 🆘 **Support**
1. Check logs: `eb logs`
2. Check health: `eb health`
3. Check config: `eb printenv`
4. Review: `DEPLOYMENT_GUIDE_STABLE.md`

