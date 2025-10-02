# 🔒 WebSocket SSL Configuration Guide

**Status:** ⚠️ WebSocket temporarily disabled in production  
**Reason:** Browser security blocks `ws://` connections from HTTPS pages  
**Solution:** Configure SSL certificate for secure WebSocket (`wss://`)

---

## 🚨 Current Issue

### Error in Production:
```
SecurityError: Failed to construct 'WebSocket': 
An insecure WebSocket connection may not be initiated from a page loaded over HTTPS.
```

### Why This Happens:
- **Frontend:** Served over HTTPS (CloudFront: `https://d2dk8wkh2d0mmy.cloudfront.net`)
- **Backend:** HTTP only (`http://political-analyst-backend-v3...`)
- **WebSocket:** Using `ws://` (insecure protocol)
- **Browser:** Blocks mixed content (HTTPS → WS) for security

---

## ✅ Temporary Fix Applied

### Changes Made:
1. **Disabled WebSocket in production** (`Frontend_v2/src/config.ts`)
   ```typescript
   wsUrl: isProd ? '' : 'ws://localhost:8001/ws/analyze'
   ```

2. **Added safety check** (`Frontend_v2/src/services/WebSocketService.ts`)
   ```typescript
   if (!this.url || this.url.trim() === '') {
     console.warn('⚠️ WebSocket disabled: SSL certificate required');
     return;
   }
   ```

3. **REST API still works** for non-streaming queries

### What Still Works:
✅ REST API endpoints (`/api/analyze`, `/api/graph/*`)  
✅ Execution graph visualization  
✅ Citations and artifacts  
✅ Local development (uses `ws://localhost:8001`)

### What Doesn't Work (Production Only):
❌ Real-time streaming responses  
❌ Progress updates during query processing  
❌ WebSocket-based chat

---

## 🔧 Permanent Solution: Enable SSL

### Option 1: Application Load Balancer (Recommended)

#### Step 1: Get SSL Certificate
```bash
# Request certificate from AWS Certificate Manager (ACM)
aws acm request-certificate \
  --domain-name "analyst-api.yourdomain.com" \
  --validation-method DNS \
  --region us-east-1
```

#### Step 2: Validate Certificate
- Go to AWS ACM Console
- Copy CNAME records
- Add to your DNS provider (e.g., Route 53, GoDaddy, Cloudflare)
- Wait for validation (~5-30 minutes)

#### Step 3: Create Load-Balanced Environment
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/backend_v2

# Create new environment with load balancer
eb create political-analyst-backend-ssl \
  --elb-type application \
  --instance-type t3.small \
  --min-instances 1 \
  --max-instances 2 \
  --envvars PORT=8000,ENABLE_QUERY_CACHE=false
```

#### Step 4: Configure HTTPS Listener
```bash
# Get Load Balancer ARN
LB_ARN=$(aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?contains(LoadBalancerName, 'political')].LoadBalancerArn" \
  --output text)

# Get Certificate ARN
CERT_ARN=$(aws acm list-certificates \
  --query "CertificateSummaryList[?DomainName=='analyst-api.yourdomain.com'].CertificateArn" \
  --output text)

# Add HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn $LB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

#### Step 5: Update Frontend Config
```typescript
// Frontend_v2/src/config.ts
export const config = {
  apiUrl: isProd 
    ? 'https://analyst-api.yourdomain.com'
    : 'http://localhost:8001',
  
  wsUrl: isProd
    ? 'wss://analyst-api.yourdomain.com/ws/analyze'  // Now secure!
    : 'ws://localhost:8001/ws/analyze',
};
```

#### Step 6: Rebuild & Deploy
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2/Frontend_v2
npm run build
aws s3 sync dist/ s3://tavily-research-frontend-1759377613/ --delete
aws cloudfront create-invalidation --distribution-id E1YO4Y7KXANJNR --paths "/*"
```

---

### Option 2: CloudFlare Tunnel (Free SSL)

If you don't have a custom domain, use CloudFlare Tunnel:

#### Step 1: Install cloudflared
```bash
brew install cloudflare/cloudflare/cloudflared
```

#### Step 2: Authenticate
```bash
cloudflared tunnel login
```

#### Step 3: Create Tunnel
```bash
cloudflared tunnel create political-analyst-backend
```

#### Step 4: Configure Tunnel
```yaml
# ~/.cloudflared/config.yml
tunnel: <TUNNEL_ID>
credentials-file: /Users/<USER>/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: analyst-api.yourdomain.com
    service: http://political-analyst-backend-v3.eba-tf2vrc23.us-east-1.elasticbeanstalk.com:80
  - service: http_status:404
```

#### Step 5: Run Tunnel
```bash
cloudflared tunnel run political-analyst-backend
```

---

### Option 3: Self-Signed Certificate (Development Only)

**⚠️ NOT recommended for production** (browsers will show warnings)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes
```

---

## 📋 Estimated Costs (Option 1)

| Resource | Cost | Notes |
|----------|------|-------|
| Application Load Balancer | ~$16/month | Base cost |
| SSL Certificate (ACM) | **FREE** | Managed by AWS |
| Data Transfer | ~$0.01/GB | Outbound traffic |
| EC2 Instance (t3.small) | $15/month | Same as before |
| **Total** | **~$31/month** | vs $15/month single instance |

---

## 🧪 Testing After Setup

```bash
# Test HTTPS endpoint
curl https://analyst-api.yourdomain.com/health

# Test WebSocket (using wscat)
npm install -g wscat
wscat -c wss://analyst-api.yourdomain.com/ws/analyze
```

---

## 📚 Additional Resources

- [AWS ACM Documentation](https://docs.aws.amazon.com/acm/)
- [Elastic Beanstalk Load Balancer](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environments-cfg-alb.html)
- [CloudFlare Tunnel Guide](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [WebSocket Security Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

---

## 🎯 Quick Decision Matrix

| Scenario | Recommended Option | Time to Setup |
|----------|-------------------|---------------|
| Have custom domain | Option 1 (ALB + ACM) | ~30 min |
| No custom domain | Option 2 (CloudFlare) | ~15 min |
| Just testing | Use localhost | 0 min |
| Production app | Option 1 (ALB + ACM) | ~30 min |

---

**Next Steps:**
1. Choose your preferred option
2. Follow the setup guide
3. Update frontend `config.ts` with `wss://` URL
4. Rebuild and deploy frontend
5. Test WebSocket connection

---

**Questions?** Contact: [Your Support Email]  
**Last Updated:** October 2, 2025

