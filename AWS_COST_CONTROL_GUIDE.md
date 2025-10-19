# AWS Cost Control & Automatic Cleanup Guide

## 📊 Current Optimizations Applied

### ✅ Completed (October 2, 2025)

1. **Instance Downsizing**
   - Changed from: `t3.small` ($15/month)
   - Changed to: `t3.micro` ($7.50/month)
   - **Savings: $7.50/month**

2. **S3 Lifecycle Policy**
   - Auto-delete artifacts older than 30 days
   - Prevents unbounded storage growth
   - **Savings: $0.30+/month (growing)**

3. **Removed Old Environments**
   - Terminated: `political-analyst-backend-v3`
   - Terminated: `political-analyst-backend-prod`
   - **Savings: $66/month**

---

## 💰 Current Monthly Cost Estimate

| Service | Resource | Monthly Cost |
|---------|----------|--------------|
| **EC2** | t3.micro instance | $7.50 |
| **Load Balancer** | Application LB | $16.00 |
| **CloudFront** | 2 distributions | $2-10 |
| **S3** | Storage (with lifecycle) | $0.50 |
| **MongoDB** | Atlas free tier | $0 |
| **TOTAL** | | **~$26-34/month** |

**Previous cost:** ~$103/month  
**New cost:** ~$30/month  
**Total savings:** ~$73/month (71% reduction) ✅

---

## 🤖 Automatic Cost Control

### 1. Cost Control Script

The script `scripts/aws-cost-control.sh` helps identify and manage expensive resources.

**Usage:**

```bash
# Dry run (check only, don't delete)
./scripts/aws-cost-control.sh

# Check resources older than 60 days
AWS_CLEANUP_DAYS=60 ./scripts/aws-cost-control.sh

# Actually delete resources (BE CAREFUL!)
DRY_RUN=false AWS_CLEANUP_DAYS=30 ./scripts/aws-cost-control.sh
```

**What it checks:**
- ✅ Elastic Beanstalk environments older than X days
- ✅ Unused load balancers
- ✅ S3 buckets without lifecycle policies
- ✅ CloudFront distributions
- ✅ Standalone EC2 instances
- ✅ Current month's estimated cost

**Recommended schedule:** Run weekly or monthly

---

### 2. AWS Budget Alerts

Set up automatic email alerts when costs exceed thresholds.

**Step 1: Update notification email**

```bash
# Edit this file and replace "your-email@example.com" with your actual email
vim scripts/aws-budget-notifications.json
```

**Step 2: Get your AWS Account ID**

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your AWS Account ID: $AWS_ACCOUNT_ID"
```

**Step 3: Create budget**

```bash
# Create a $50/month budget with alerts at 80% and 100%
aws budgets create-budget \
  --account-id $AWS_ACCOUNT_ID \
  --budget file://scripts/aws-budget-config.json \
  --notifications-with-subscribers file://scripts/aws-budget-notifications.json
```

**You'll receive emails when:**
- ✉️ 80% of budget is reached ($40 of $50)
- ✉️ 100% of budget is reached ($50)
- ✉️ Forecasted to exceed budget

---

### 3. S3 Lifecycle Policies

**Already implemented** for artifacts bucket. Here's how to apply to other buckets:

```bash
# For any bucket, create lifecycle policy
cat > /tmp/lifecycle.json << 'EOF'
{
  "Rules": [
    {
      "ID": "DeleteOldFiles",
      "Status": "Enabled",
      "Filter": {
        "Prefix": ""
      },
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
EOF

# Apply to bucket
aws s3api put-bucket-lifecycle-configuration \
  --bucket YOUR_BUCKET_NAME \
  --lifecycle-configuration file:///tmp/lifecycle.json
```

**Customization:**

- `Days: 30` - Delete files older than 30 days
- `Days: 90` - Delete files older than 90 days
- `Prefix: "logs/"` - Only delete files in "logs/" folder

---

### 4. AWS Cost Anomaly Detection

Automatically detect unusual spending patterns.

**Setup (via Console):**

1. Go to: https://console.aws.amazon.com/cost-management/home#/anomaly-detection
2. Click "Create monitor"
3. Select "AWS services" (all services)
4. Set alert threshold: $5
5. Add your email

**Or via CLI:**

```bash
# Create cost anomaly monitor
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "PoliticalAnalystMonitor",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'
```

---

### 5. Automatic Instance Scheduling (Optional)

**Stop EC2 instances during non-business hours to save ~50% on compute costs.**

Not implemented yet, but here's how:

```bash
# Install AWS Instance Scheduler
# Stops instances at night/weekends
# See: https://aws.amazon.com/solutions/implementations/instance-scheduler/
```

**Savings potential:** ~$3-4/month (if stopped 12 hours/day)

---

## 🚨 High-Cost Resources to Monitor

### Elastic Beanstalk Environments

**Cost:** ~$34/month per environment

```bash
# List all environments
aws elasticbeanstalk describe-environments \
  --query 'Environments[*].{Name:EnvironmentName,Status:Status,Created:DateCreated}' \
  --output table

# Terminate unused environment
aws elasticbeanstalk terminate-environment \
  --environment-name OLD_ENVIRONMENT_NAME \
  --terminate-resources
```

### Application Load Balancers

**Cost:** ~$16/month per ALB

```bash
# List all load balancers
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[*].{Name:LoadBalancerName,Created:CreatedTime}' \
  --output table

# Delete unused load balancer (CAREFUL!)
aws elbv2 delete-load-balancer --load-balancer-arn ARN_HERE
```

### CloudFront Distributions

**Cost:** ~$1-5/month per distribution (traffic-based)

```bash
# List distributions
aws cloudfront list-distributions \
  --query 'DistributionList.Items[*].{ID:Id,Domain:DomainName,Enabled:Enabled}' \
  --output table

# Disable distribution (stops charges)
# Must be done via console or update-distribution API
```

### S3 Storage

**Cost:** $0.023/GB/month

```bash
# Check bucket sizes
aws s3 ls | awk '{print $3}' | while read bucket; do
  size=$(aws s3 ls s3://$bucket --recursive --summarize 2>/dev/null | grep "Total Size" | awk '{print $3}')
  size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc 2>/dev/null || echo "0")
  echo "$bucket: ${size_mb}MB"
done
```

---

## 📅 Maintenance Schedule

### Daily
- Monitor AWS Budget Alerts (email)
- Check Cost Anomaly Detection (email)

### Weekly
```bash
# Run cost control script (dry run)
./scripts/aws-cost-control.sh
```

### Monthly
```bash
# Review AWS Cost Explorer
# https://console.aws.amazon.com/cost-management/home#/cost-explorer

# Actual cleanup (after review)
DRY_RUN=false AWS_CLEANUP_DAYS=30 ./scripts/aws-cost-control.sh

# Review unused resources
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

## 🎯 Future Optimizations (Not Implemented)

### Option: Remove Load Balancer
**Savings:** $16/month (50% additional savings)

```bash
# Switch to single instance (no load balancer)
eb config political-analyst-backend-lb
# Change: EnvironmentType: LoadBalanced → SingleInstance
# Save and redeploy

# Update CloudFront origin to point directly to EC2 instance
```

**Pros:**
- Biggest additional savings
- CloudFront provides HTTPS termination

**Cons:**
- No auto-scaling
- Single point of failure

**Recommended for:** Demo/development environments only

### Option: Reserved Instances
**Savings:** ~30% on compute costs (if running 24/7)

- Not recommended for short-term projects
- Requires 1-year commitment

### Option: Spot Instances
**Savings:** ~70% on compute costs

- Not available for Elastic Beanstalk easily
- Can be terminated anytime

---

## 📊 Cost Tracking Tools

### AWS Cost Explorer
https://console.aws.amazon.com/cost-management/home#/cost-explorer

### AWS Billing Dashboard
https://console.aws.amazon.com/billing/home

### CLI: Get Current Month Cost
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --output json | jq '.ResultsByTime[0].Total.UnblendedCost.Amount'
```

---

## ⚠️ Important Notes

1. **S3 Lifecycle Deletion is Permanent**
   - Artifacts >30 days old are automatically deleted
   - Ensure you don't need historical data before setting short expiration

2. **Budget Alerts are Estimates**
   - Actual costs may vary
   - Some services have delayed billing

3. **Always Test in Dry Run Mode First**
   - The cost control script defaults to dry run
   - Review what will be deleted before setting `DRY_RUN=false`

4. **Load Balancer Removal Requires Downtime**
   - ~5-10 minutes during the switch
   - Update CloudFront origin after change

---

## 🆘 Emergency Cost Reduction

If costs spike unexpectedly:

```bash
# 1. Stop EC2 instances (not terminate)
eb config political-analyst-backend-lb
# Set: MinSize: 0, MaxSize: 0

# 2. Disable CloudFront (via console)

# 3. Check for anomalies
aws ce get-anomalies \
  --date-interval Start=2025-10-01,End=2025-10-31 \
  --max-results 10

# 4. Review top services by cost
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

## 📞 Support

- **AWS Support:** https://console.aws.amazon.com/support/home
- **Cost Optimization:** https://aws.amazon.com/pricing/cost-optimization/
- **Billing FAQ:** https://aws.amazon.com/premiumsupport/knowledge-center/

---

**Last Updated:** October 2, 2025  
**Current Monthly Cost:** ~$30/month  
**Optimization Status:** ✅ Optimized (71% reduction from original $103/month)

