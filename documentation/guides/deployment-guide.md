# Complete Deployment Guide

## 🎯 **Prerequisites**

### **Required Accounts & Tools**
- AWS Account with billing enabled
- MongoDB Atlas account (free tier sufficient)
- Domain name (optional, for custom URLs)

### **Required API Keys**
- Tavily API Key (from https://tavily.com)
- OpenAI API Key (from https://platform.openai.com)

### **Local Tools**
```bash
# Install AWS CLI
pip install awscli awsebcli

# Configure AWS
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)
```

## 🗄 **Phase 1: Database Setup (MongoDB Atlas)**

### **Step 1: Create Cluster**
1. Go to https://cloud.mongodb.com
2. Create account or sign in
3. Create new project: "Web Research Agent"
4. Build database → Shared (FREE)
5. Cloud Provider: AWS, Region: us-east-1
6. Cluster Name: "web-research-agent"

### **Step 2: Security Configuration**
```bash
# Database Access
Username: api_user
Password: [generate strong password - save this!]
Role: Read and write to any database

# Network Access  
IP Address: 0.0.0.0/0 (allow from anywhere)
# Note: In production, restrict to your AWS EB IPs
```

### **Step 3: Get Connection String**
```
mongodb+srv://api_user:<password>@web-research-agent.xxxxx.mongodb.net/?retryWrites=true&w=majority
```
**Save this connection string - you'll need it for the backend deployment.**

## 🏗 **Phase 2: Backend Deployment (AWS Elastic Beanstalk)**

### **Step 1: Prepare Application**
```bash
cd backend/

# Create application.py (EB entry point)
cat > application.py << 'EOF'
#!/usr/bin/env python3
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
EOF

# Ensure requirements.txt includes production dependencies
echo "gunicorn==20.1.0" >> requirements.txt
echo "flask-cors==4.0.0" >> requirements.txt
echo "python-json-logger==2.0.4" >> requirements.txt
```

### **Step 2: Create EB Configuration**
```bash
# Create .ebextensions directory
mkdir -p .ebextensions

# Python configuration
cat > .ebextensions/python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 10
    Availability Zones: Any 2
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Unit: Percent
    UpperThreshold: 80
    LowerThreshold: 20
    ScaleUpIncrement: 2
    ScaleDownIncrement: -1
  aws:elasticbeanstalk:healthreporting:system:
    SystemType: enhanced
    HealthCheckSuccessThreshold: Ok
    HealthCheckURL: /health
EOF

# Logging configuration
cat > .ebextensions/logging.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:cloudwatch:logs:
    StreamLogs: true
    DeleteOnTerminate: false
    RetentionInDays: 7
EOF
```

### **Step 3: Deploy to Elastic Beanstalk**
```bash
# Initialize EB application
eb init

# Choose options:
# - Select region: us-east-1
# - Application name: web-research-agent
# - Platform: Python
# - Platform version: Python 3.9 running on 64bit Amazon Linux 2
# - Setup SSH: No (unless needed for debugging)

# Create environment
eb create production

# Choose options:
# - Environment name: production
# - DNS CNAME prefix: [unique-name] (e.g., web-research-agent-prod)
# - Load balancer type: application

# This will take 5-10 minutes to deploy...
```

### **Step 4: Configure Environment Variables**
```bash
# Set production environment variables
eb setenv \
  TAVILY_API_KEY=your-actual-tavily-key \
  OPENAI_API_KEY=your-actual-openai-key \
  MONGODB_CONNECTION_STRING="mongodb+srv://api_user:your-password@web-research-agent.xxxxx.mongodb.net/" \
  FLASK_ENV=production \
  CORS_ORIGINS=https://your-frontend-domain.cloudfront.net

# Deploy with new environment variables
eb deploy

# Check deployment status
eb status
eb health
```

### **Step 5: Verify Backend Deployment**
```bash
# Get your backend URL
eb status | grep CNAME

# Test health endpoint
curl https://your-backend-url.elasticbeanstalk.com/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-09-27T10:30:00Z",
#   "agent_initialized": true,
#   "version": "1.0.0"
# }

# Test research endpoint
curl -X POST https://your-backend-url.elasticbeanstalk.com/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

## 🎨 **Phase 3: Frontend Deployment (AWS S3 + CloudFront)**

### **Step 1: Prepare Frontend**
```bash
cd frontend/

# Create production environment file
cat > .env.production << 'EOF'
REACT_APP_API_URL=https://your-backend-url.elasticbeanstalk.com
REACT_APP_ENVIRONMENT=production
EOF

# Update package.json homepage (optional)
npm pkg set homepage="https://your-frontend-domain.cloudfront.net"

# Build for production
npm run build
```

### **Step 2: Create S3 Bucket**
```bash
# Create unique bucket name
BUCKET_NAME="web-research-agent-frontend-$(date +%s)"
echo "Using bucket name: $BUCKET_NAME"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Configure for static website hosting
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document index.html

# Upload build files
aws s3 sync build/ s3://$BUCKET_NAME --delete

# Make bucket public for website hosting
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
```

### **Step 3: Create CloudFront Distribution**
```bash
# Create distribution configuration
cat > cloudfront-config.json << EOF
{
  "CallerReference": "web-research-agent-$(date +%s)",
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "S3-frontend",
      "DomainName": "$BUCKET_NAME.s3.amazonaws.com",
      "S3OriginConfig": {
        "OriginAccessIdentity": ""
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [{
      "ErrorCode": 404,
      "ResponsePagePath": "/index.html",
      "ResponseCode": "200",
      "ErrorCachingMinTTL": 10
    }]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
EOF

# Create CloudFront distribution
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json

# Note: CloudFront deployment takes 10-15 minutes
# Save the distribution domain name from the output
```

### **Step 4: Update Backend CORS**
```bash
# Update backend CORS with CloudFront domain
eb setenv CORS_ORIGINS=https://your-cloudfront-domain.cloudfront.net

# Redeploy backend
eb deploy
```

## ✅ **Phase 4: Verification & Testing**

### **Step 1: Health Checks**
```bash
# Test backend health
curl https://your-backend-url.elasticbeanstalk.com/health

# Expected response:
{
  "status": "healthy",
  "agent_initialized": true,
  "version": "1.0.0",
  "environment": "production"
}

# Test research API with timeout
curl -X POST https://your-backend-url.elasticbeanstalk.com/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?"}' \
  --max-time 120

# Should return query_id for async processing
```

### **Step 2: Frontend Verification**
```bash
# Test frontend access
curl -I https://your-cloudfront-domain.cloudfront.net

# Expected: 200 OK response with HTML content-type

# Test frontend in browser - verify:
# 1. Page loads correctly
# 2. Can submit research queries
# 3. Results display properly
# 4. Export functionality works
```

### **Step 3: End-to-End Testing**
1. **Submit Test Query:**
   - Open frontend URL in browser
   - Submit query: "What are the latest developments in artificial intelligence?"
   - Verify processing indicator appears
   - Wait for results (should complete in 60-90 seconds)

2. **Verify Database Storage:**
   ```bash
   # Check MongoDB Atlas dashboard
   # Verify queries and results collections have data
   ```

3. **Test Export Functionality:**
   - Try exporting results in JSON, CSV, and PDF formats
   - Verify files download correctly

4. **Test Mobile Responsiveness:**
   - Test on mobile device or browser dev tools
   - Verify UI adapts properly

## 🔧 **Troubleshooting**

### **Common Backend Issues**

#### **EB Deployment Fails**
```bash
# Check detailed logs
eb logs --all

# SSH to instance for debugging
eb ssh

# Check application process
sudo systemctl status web-research-agent

# Check Python application logs
sudo tail -f /var/log/eb-engine.log
```

#### **Agent Initialization Fails**
```bash
# Check environment variables
eb printenv

# Verify API keys are set correctly
# Check if MongoDB connection string is valid
```

#### **High CPU Usage / Scaling Issues**
```bash
# Check current scaling configuration
eb config

# Update auto-scaling thresholds if needed
eb config save --cfg production-config
# Edit .elasticbeanstalk/saved_configs/production-config.cfg.yml
# Then apply: eb config put production-config
```

### **Common Frontend Issues**

#### **CloudFront Cache Issues**
```bash
# Invalidate cache after deployment
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"

# Check invalidation status
aws cloudfront list-invalidations --distribution-id YOUR_DISTRIBUTION_ID
```

#### **CORS Errors**
```bash
# Verify backend CORS settings
curl -H "Origin: https://your-frontend-domain.cloudfront.net" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-backend-url.elasticbeanstalk.com/research
```

### **Database Connection Issues**
- Verify MongoDB connection string format
- Check network access settings (IP whitelist)
- Ensure database user has correct permissions
- Test connection from backend server

## 📊 **Monitoring & Maintenance**

### **Set Up CloudWatch Alarms**
```bash
# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name "EB-HighErrorRate" \
  --alarm-description "High error rate in Elastic Beanstalk" \
  --metric-name "4XXError" \
  --namespace "AWS/ELB" \
  --statistic "Sum" \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold

# Create alarm for high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name "EB-HighCPU" \
  --alarm-description "High CPU utilization" \
  --metric-name "CPUUtilization" \
  --namespace "AWS/EC2" \
  --statistic "Average" \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold
```

### **Regular Maintenance Tasks**
1. **Weekly:** Check application logs for errors
2. **Weekly:** Review MongoDB usage and performance
3. **Monthly:** Update security patches with `eb deploy`
4. **Monthly:** Review and optimize CloudWatch costs
5. **Quarterly:** Review and update API keys

## 🎯 **Production Optimization**

### **Performance Tuning**
```python
# backend/config.py - Production settings
PRODUCTION_CONFIG = {
    "GUNICORN_WORKERS": 4,
    "GUNICORN_TIMEOUT": 120,
    "MONGODB_MAX_POOL_SIZE": 50,
    "MONGODB_MIN_POOL_SIZE": 10,
    "REDIS_CONNECTION_POOL": 20,
    "LOG_LEVEL": "INFO"
}
```

### **Security Hardening**
- Enable AWS WAF on CloudFront
- Implement IP whitelisting for admin endpoints
- Set up SSL certificate monitoring
- Enable VPC for Elastic Beanstalk (for enhanced security)

## 🎯 **Post-Deployment Checklist**

- [ ] Backend health check responding (200 OK)
- [ ] Frontend loading correctly via CloudFront
- [ ] Database connection working
- [ ] Research queries completing successfully (60-90s)
- [ ] Export functionality working (JSON, CSV, PDF)
- [ ] Mobile responsiveness verified
- [ ] Error handling tested with invalid inputs
- [ ] Load testing completed (50+ concurrent users)
- [ ] CloudWatch monitoring active
- [ ] SSL certificates valid
- [ ] All API keys secured and rotated

---

## 🚀 **Success! Your Web Research Agent is Live**

Your multi-agent research system is now running in production with:
- ✅ **Backend:** Multi-instance AWS deployment with auto-scaling
- ✅ **Frontend:** CloudFront-distributed React application  
- ✅ **Database:** MongoDB Atlas with analytics
- ✅ **Monitoring:** CloudWatch alerts and logging

**Next Steps:**
1. Record your demo video using the live production system
2. Share the URLs with stakeholders
3. Monitor performance and scale as needed

**Production URLs:**
- **Frontend:** https://your-cloudfront-domain.cloudfront.net
- **Backend API:** https://your-backend-url.elasticbeanstalk.com
- **API Documentation:** https://your-backend-url.elasticbeanstalk.com/docs
