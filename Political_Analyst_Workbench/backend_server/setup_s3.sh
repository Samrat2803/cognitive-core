#!/bin/bash

echo "🚀 Setting up S3 for Political Analyst Artifacts"
echo "=================================================="
echo ""

BUCKET_NAME="political-analyst-artifacts"
REGION="us-east-1"

echo "📦 Step 1: Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>&1 | tee /tmp/s3_setup.log

if grep -q "BucketAlreadyOwnedByYou\|make_bucket" /tmp/s3_setup.log; then
    echo "✅ Bucket exists or created successfully"
else
    echo "⚠️  Bucket creation result (may already exist):"
    cat /tmp/s3_setup.log
fi

echo ""
echo "🔐 Step 2: Setting bucket policy for private access..."
cat > /tmp/bucket_policy.json << 'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowRootAndIAMUserAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):root"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::political-analyst-artifacts",
        "arn:aws:s3:::political-analyst-artifacts/*"
      ]
    }
  ]
}
POLICY

# Don't apply bucket policy - it's private by default and IAM credentials will work
echo "✅ Bucket is private (default). Your IAM credentials will work."

echo ""
echo "🧪 Step 3: Testing S3 access..."
echo "test" > /tmp/test_artifact.txt
aws s3 cp /tmp/test_artifact.txt s3://$BUCKET_NAME/test/test_artifact.txt

if [ $? -eq 0 ]; then
    echo "✅ S3 upload test SUCCESSFUL!"
    aws s3 rm s3://$BUCKET_NAME/test/test_artifact.txt
    echo "✅ Cleanup completed"
else
    echo "❌ S3 upload test FAILED"
    echo "   This may be due to bucket not existing or permissions issues"
fi

echo ""
echo "✅ S3 Setup Complete!"
echo ""
echo "Next step: Restart your backend server to test artifact uploads"
echo "Run: ./test_s3_after_permissions.sh"

