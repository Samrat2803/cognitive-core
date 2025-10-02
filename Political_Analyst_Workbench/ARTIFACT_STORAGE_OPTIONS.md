# Free Artifact Storage Options

Complete guide to free storage solutions for Political Analyst artifacts (charts, visualizations).

---

## 📊 Storage Requirements

**Per Artifact:**
- HTML: ~4-5 MB (Plotly interactive charts)
- PNG: ~50-200 KB (static images)
- **Total per artifact: ~5 MB**

**Estimated Usage:**
- 10 sessions/day = 50 MB/day = 1.5 GB/month
- 100 sessions/day = 500 MB/day = 15 GB/month

---

## 🆓 Free Storage Options

### Option 1: MongoDB Atlas + GridFS (RECOMMENDED)
**Best for: Small to medium scale, integrated database**

✅ **Pros:**
- **Free Tier:** 512 MB storage
- Already using MongoDB for metadata
- GridFS handles files > 16MB automatically
- No additional setup needed
- Files stored with

 metadata
- Easy backup/restore

❌ **Cons:**
- Limited to 512 MB total (including database)
- ~100 artifacts max (if 5MB each)
- Shared performance on free tier

**Setup:**
```python
# Already included in mongo_service.py!
await mongo_service.upload_artifact_file(
    artifact_id="line_abc123",
    file_content=html_bytes,
    filename="chart.html",
    content_type="text/html"
)
```

**Cost:** 
- Free: 512 MB
- Paid: $9/month (M2) - 2GB storage
- Paid: $25/month (M5) - 5GB storage

---

### Option 2: AWS S3 Free Tier
**Best for: Scalability and production use**

✅ **Pros:**
- **Free Tier:** 5 GB storage (first 12 months)
- 20,000 GET requests/month
- 2,000 PUT requests/month
- Industry standard, reliable
- Easy CDN integration (CloudFront)
- Signed URLs for secure access

❌ **Cons:**
- Free only for 12 months
- After free tier: $0.023/GB/month ($0.12 for 5GB)
- Requires AWS account setup
- Additional code for uploads

**Setup:**
```python
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

# Upload artifact
s3_client.upload_fileobj(
    file_content,
    'political-analyst-artifacts',
    f'{artifact_id}.html',
    ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'}
)

# Get URL
url = f"https://political-analyst-artifacts.s3.amazonaws.com/{artifact_id}.html"
```

**Cost After Free Tier:**
- Storage: $0.023/GB/month
- Requests: $0.0004/1000 GET, $0.005/1000 PUT
- **Example:** 10GB + 100k requests = $0.27/month

---

### Option 3: Cloudinary Free Tier
**Best for: Image-heavy use case**

✅ **Pros:**
- **Free Tier:** 25 GB storage + 25 GB bandwidth
- Optimized for images/media
- Automatic image optimization
- CDN included
- Transformations (resize, crop, etc.)
- Forever free (not just 12 months)

❌ **Cons:**
- Primarily for images (PNG works, HTML needs workaround)
- 10 MB file size limit
- Not ideal for HTML files
- Limited to media files

**Setup:**
```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Upload PNG
result = cloudinary.uploader.upload(
    png_content,
    public_id=f"artifacts/{artifact_id}",
    resource_type="image"
)

url = result['secure_url']
```

**Cost:**
- Free: 25 GB storage + 25 GB bandwidth
- Paid: $99/month - 65 GB + 65 GB bandwidth

---

### Option 4: Vercel Blob Storage
**Best for: Next.js/Vercel deployments**

✅ **Pros:**
- **Free Tier:** 500 MB storage
- Simple API
- Automatic CDN
- Good for Vercel-hosted frontends
- Fast global distribution

❌ **Cons:**
- Only 500 MB free
- Tied to Vercel ecosystem
- $0.15/GB after free tier

**Setup:**
```javascript
// Next.js/Vercel
import { put } from '@vercel/blob';

const blob = await put(`artifacts/${artifactId}.html`, file, {
  access: 'public',
  contentType: 'text/html'
});

const url = blob.url;
```

**Cost:**
- Free: 500 MB
- Paid: $0.15/GB/month

---

### Option 5: GitHub Releases (Creative Solution)
**Best for: Open source projects**

✅ **Pros:**
- **Free:** Unlimited for public repos
- 2 GB per file limit
- Permanent storage
- Version controlled

❌ **Cons:**
- Not designed for this use case
- Requires public repository
- Manual release management
- Not a proper CDN

---

## 🎯 Recommendation Matrix

| Use Case | Storage | Monthly Cost | Best Option |
|----------|---------|--------------|-------------|
| **MVP/Development** | < 500 MB | Free | MongoDB GridFS |
| **Small Production** | 1-5 GB | Free (12mo) | AWS S3 Free Tier |
| **Image-Heavy** | < 25 GB | Free Forever | Cloudinary |
| **Vercel Frontend** | < 500 MB | Free | Vercel Blob |
| **Budget Production** | 10 GB | $0.23/mo | AWS S3 |
| **Enterprise** | 100+ GB | ~$3/mo | AWS S3 + CloudFront |

---

## 🏗️ Hybrid Approach (RECOMMENDED)

**Best of both worlds:**

1. **MongoDB GridFS** - Store recent artifacts (last 7 days)
2. **AWS S3** - Archive older artifacts
3. **Cloudinary** - Serve PNG images

**Benefits:**
- Fast access to recent data (MongoDB)
- Unlimited history (S3)
- Optimized image delivery (Cloudinary)
- Total cost: ~$0.50/month for 20GB

**Implementation:**
```python
class ArtifactStorage:
    def __init__(self):
        self.mongo = mongo_service
        self.s3_client = boto3.client('s3')
        self.cloudinary = cloudinary
    
    async def save_artifact(self, artifact_id, html_content, png_content):
        # Save to MongoDB GridFS (hot storage)
        html_file_id = await self.mongo.upload_artifact_file(
            artifact_id, html_content, f"{artifact_id}.html", "text/html"
        )
        
        # Save PNG to Cloudinary (optimized delivery)
        cloudinary_result = cloudinary.uploader.upload(
            png_content, public_id=f"artifacts/{artifact_id}"
        )
        
        # Save metadata
        await self.mongo.save_artifact_metadata(ArtifactMetadata(
            artifact_id=artifact_id,
            html_file_id=html_file_id,
            png_url=cloudinary_result['secure_url']
        ))
    
    async def archive_old_artifacts(self):
        """Move artifacts older than 7 days to S3"""
        cutoff = datetime.utcnow() - timedelta(days=7)
        old_artifacts = await self.mongo.db.artifacts.find(
            {'created_at': {'$lt': cutoff}, 'html_file_id': {'$exists': True}}
        ).to_list(length=100)
        
        for artifact in old_artifacts:
            # Download from GridFS
            content = await self.mongo.download_artifact_file(artifact['html_file_id'])
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket='political-analyst-archive',
                Key=f"{artifact['artifact_id']}.html",
                Body=content
            )
            
            # Update metadata (remove GridFS ID, add S3 URL)
            await self.mongo.db.artifacts.update_one(
                {'artifact_id': artifact['artifact_id']},
                {'$set': {
                    'html_url': f"https://s3.amazonaws.com/political-analyst-archive/{artifact['artifact_id']}.html",
                    'html_file_id': None,
                    'archived': True
                }}
            )
            
            # Delete from GridFS to free space
            await self.mongo.gridfs.delete(artifact['html_file_id'])
```

---

## 📝 Setup Instructions

### MongoDB Atlas Setup (Free 512 MB)

1. **Create Account:** https://www.mongodb.com/cloud/atlas/register
2. **Create Cluster:**
   - Choose "M0 Sandbox" (Free)
   - Select region closest to your users
   - Cluster name: "political-analyst"
3. **Configure Access:**
   - Database Access: Create user with password
   - Network Access: Add IP (0.0.0.0/0 for development)
4. **Get Connection String:**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/political_analyst_db
   ```
5. **Add to .env:**
   ```bash
   MONGODB_CONNECTION_STRING=mongodb+srv://...
   DATABASE_NAME=political_analyst_db
   ```

### AWS S3 Setup (Free 5 GB for 12 months)

1. **Create AWS Account:** https://aws.amazon.com/free/
2. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://political-analyst-artifacts --region us-east-1
   ```
3. **Set Bucket Policy (Public Read):**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::political-analyst-artifacts/*"
     }]
   }
   ```
4. **Create IAM User:**
   - IAM > Users > Add User
   - Attach policy: `AmazonS3FullAccess`
   - Save Access Key ID and Secret
5. **Add to .env:**
   ```bash
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_S3_BUCKET=political-analyst-artifacts
   AWS_REGION=us-east-1
   ```

### Cloudinary Setup (Free 25 GB)

1. **Create Account:** https://cloudinary.com/users/register/free
2. **Get Credentials:** Dashboard > Account Details
3. **Add to .env:**
   ```bash
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

---

## 💰 Cost Comparison (10 GB Storage)

| Solution | Monthly Cost | Annual Cost | Free Tier |
|----------|--------------|-------------|-----------|
| MongoDB GridFS | $25 (M5 cluster) | $300 | 512 MB free |
| AWS S3 | $0.23 | $2.76 | 5 GB free (12mo) |
| Cloudinary | $0 | $0 | 25 GB free forever |
| Hybrid (Recommended) | $0.23 | $2.76 | Mix of free tiers |

**Winner for Budget:** Cloudinary (PNG only) + MongoDB GridFS (HTML metadata)  
**Winner for Scale:** AWS S3  
**Winner for Simplicity:** MongoDB GridFS

---

## 🚀 Implementation Priority

### Phase 1: MVP (Use MongoDB GridFS)
- ✅ Already coded in `mongo_service.py`
- ✅ Simple, integrated
- ✅ 512 MB free = ~100 artifacts
- ✅ Perfect for development/testing

### Phase 2: Add Cloudinary (PNG Images)
- Upload PNG to Cloudinary
- Store URL in MongoDB
- Faster image delivery
- Free 25 GB

### Phase 3: Add S3 Archival
- Archive old artifacts (>7 days) to S3
- Keep recent in MongoDB GridFS
- Delete from GridFS after archival
- Cost-effective at scale

---

## ✅ Current Recommendation

**For your use case (MVP → Production):**

1. **Start with MongoDB GridFS**
   - Already integrated
   - 512 MB free
   - Perfect for MVP

2. **Add Cloudinary for PNG** (when > 50 artifacts)
   - Free 25 GB
   - Better image delivery
   - Easy migration

3. **Add S3 for HTML archival** (when > 100 artifacts)
   - $0.23/month for 10 GB
   - Unlimited scale
   - Professional solution

**Total Cost:**
- Months 1-3: $0 (MongoDB free tier)
- Months 4-12: $0 (still under 512 MB)
- Year 2+: ~$0.25/month (S3 for archives)

---

## 📊 Quick Start

**Use the MongoDB service already created:**

```python
from backend_server.services.mongo_service import mongo_service

# Save artifact to MongoDB GridFS
async def save_artifact(artifact_id, html_path, png_path):
    # Read files
    with open(html_path, 'rb') as f:
        html_content = f.read()
    with open(png_path, 'rb') as f:
        png_content = f.read()
    
    # Upload to GridFS
    html_file_id = await mongo_service.upload_artifact_file(
        artifact_id, html_content, f"{artifact_id}.html", "text/html"
    )
    png_file_id = await mongo_service.upload_artifact_file(
        artifact_id, png_content, f"{artifact_id}.png", "image/png"
    )
    
    # Save metadata
    await mongo_service.save_artifact_metadata(ArtifactMetadata(
        artifact_id=artifact_id,
        session_id=session_id,
        type="line_chart",
        html_file_id=html_file_id,
        png_file_id=png_file_id
    ))

# Retrieve artifact
async def get_artifact(artifact_id):
    metadata = await mongo_service.get_artifact(artifact_id)
    html_content = await mongo_service.download_artifact_file(metadata['html_file_id'])
    return html_content
```

**That's it! No additional services needed for MVP.**

---

## 🎯 Final Recommendation

**Use MongoDB Atlas Free Tier + GridFS for now.**

- ✅ Free
- ✅ Already coded
- ✅ Integrated with your database
- ✅ Supports ~100 artifacts
- ✅ Can migrate to S3/Cloudinary later

When you exceed 512 MB or need better performance, migrate to the hybrid approach with Cloudinary (images) + S3 (HTML archives).

