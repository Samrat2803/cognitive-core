# 🚀 AWS S3 + CloudFront Deployment Guide

## Prerequisites

### 1. AWS CLI Installation
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
```

### 2. AWS Credentials Configuration
```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region (us-east-1 recommended)
# - Default output format (json)
```

### 3. Required AWS Permissions
Your AWS user needs these policies:
- `AmazonS3FullAccess`
- `CloudFrontFullAccess`
- `IAMReadOnlyAccess`

## 🔧 Deployment Options

### Option 1: Automatic Deployment (Recommended)
```bash
# Run the complete deployment script
./aws-deploy.sh
```

This script will:
- ✅ Build the React app for production
- ✅ Create S3 bucket with unique name
- ✅ Configure static website hosting
- ✅ Set up public read permissions
- ✅ Upload all build files with proper caching
- ✅ Create CloudFront distribution
- ✅ Configure error handling for SPA routing

### Option 2: Manual Step-by-Step

#### Step 1: Build for Production
```bash
npm run build
```

#### Step 2: Create S3 Bucket
```bash
BUCKET_NAME="tavily-research-frontend-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1
```

#### Step 3: Configure Static Website Hosting
```bash
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html
```

#### Step 4: Set Bucket Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
        }
    ]
}
```

#### Step 5: Upload Files
```bash
# Upload static assets with long cache
aws s3 sync build/ s3://$BUCKET_NAME/ \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html"

# Upload HTML files with no cache
aws s3 sync build/ s3://$BUCKET_NAME/ \
    --cache-control "public, max-age=0, no-cache" \
    --include "*.html"
```

#### Step 6: Create CloudFront Distribution
```bash
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

## 📋 Post-Deployment Checklist

- [ ] **Frontend URL working**: Test CloudFront distribution URL
- [ ] **API Integration**: Verify API calls work from production
- [ ] **Mobile responsiveness**: Test on mobile devices
- [ ] **Export functionality**: Test JSON/CSV/PDF exports
- [ ] **Error handling**: Test offline/error scenarios
- [ ] **Performance**: Check page load speeds
- [ ] **SSL Certificate**: Verify HTTPS is working

## 🔄 Updates and Maintenance

### Update Frontend Content
```bash
# 1. Build latest changes
npm run build

# 2. Sync to S3
aws s3 sync build/ s3://YOUR_BUCKET_NAME/ --delete

# 3. Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

### Monitor and Troubleshoot
```bash
# Check CloudFront distribution status
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID

# View S3 bucket contents
aws s3 ls s3://YOUR_BUCKET_NAME/ --recursive

# Check website endpoint
curl -I http://YOUR_BUCKET_NAME.s3-website-us-east-1.amazonaws.com
```

## 🎯 Expected Results

After successful deployment:

### 🌐 **URLs Available:**
- **S3 Website**: `http://BUCKET_NAME.s3-website-us-east-1.amazonaws.com`
- **CloudFront (Production)**: `https://DISTRIBUTION_DOMAIN.cloudfront.net`

### ⚡ **Performance Features:**
- **Global CDN**: Sub-second load times worldwide
- **HTTPS**: SSL/TLS encryption enabled
- **Caching**: Optimized cache headers for static assets
- **Compression**: Gzip compression for smaller file sizes
- **SPA Support**: Proper routing for React Router

### 📊 **Monitoring:**
- **CloudWatch**: Automatic metrics collection
- **Access Logs**: S3 and CloudFront request logging
- **Error Tracking**: 4xx/5xx error monitoring

## 🚨 Troubleshooting

### Common Issues:

**1. Access Denied Errors**
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket YOUR_BUCKET_NAME
```

**2. CloudFront Not Serving Latest Content**
```bash
# Create cache invalidation
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

**3. API Calls Failing from Production**
- Verify API_URL in production config
- Check CORS settings on backend
- Ensure SSL certificates are valid

**4. 404 Errors on Direct URLs**
- Verify CloudFront error pages configuration
- Check S3 error document setting

## 💡 Cost Optimization Tips

1. **S3 Storage**: Use Standard storage class for active content
2. **CloudFront**: Consider PriceClass_100 for cost savings
3. **Monitoring**: Set up billing alerts
4. **Cleanup**: Remove old deployment artifacts regularly

---

## 🎉 Team C Deployment Complete!

Your frontend is now production-ready with:
- ✅ Global CDN distribution
- ✅ SSL/HTTPS encryption  
- ✅ Optimized caching
- ✅ SPA routing support
- ✅ Mobile responsiveness
- ✅ High availability

**Next Steps:**
1. Share the CloudFront URL with Team D for demo preparation
2. Update Team A and Team B with production frontend URL
3. Conduct final integration testing
4. Prepare for stakeholder demonstration

**Congratulations! 🎊 Team C frontend deployment is complete!**
