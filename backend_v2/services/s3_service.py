"""
AWS S3 Service for Artifact Storage
Handles uploading, downloading, and managing artifacts in S3
"""

import os
import asyncio
from typing import Optional, Tuple, Dict
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

load_dotenv()


class S3Service:
    """Handles all S3 operations for artifact storage"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "political-analyst-artifacts")
        
        if not self.access_key or not self.secret_key:
            raise ValueError("AWS credentials not found in environment")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        
        self._bucket_checked = False
    
    def _ensure_bucket_exists(self) -> bool:
        """Ensure S3 bucket exists, create if it doesn't"""
        if self._bucket_checked:
            return True
        
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket '{self.bucket_name}' exists")
            self._bucket_checked = True
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    
                    # Set bucket policy for public read access to artifacts
                    # (or keep private and use presigned URLs - recommended)
                    print(f"✅ Created S3 bucket '{self.bucket_name}'")
                    self._bucket_checked = True
                    return True
                    
                except ClientError as create_error:
                    print(f"❌ Failed to create S3 bucket: {create_error}")
                    return False
            else:
                print(f"❌ Error checking S3 bucket: {e}")
                return False
    
    async def upload_artifact(
        self,
        local_file_path: str,
        artifact_id: str,
        artifact_type: str
    ) -> Optional[str]:
        """
        Upload artifact to S3 (private by default)
        
        Args:
            local_file_path: Path to local file
            artifact_id: Unique artifact identifier
            artifact_type: Type of artifact (e.g., 'line_chart', 'bar_chart')
        
        Returns:
            S3 key if successful, None otherwise (use get_presigned_url to access)
        """
        if not self._ensure_bucket_exists():
            return None
        
        if not os.path.exists(local_file_path):
            print(f"❌ Local file not found: {local_file_path}")
            return None
        
        # Determine content type
        file_ext = os.path.splitext(local_file_path)[1].lower()
        content_type_map = {
            '.html': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.json': 'application/json'
        }
        content_type = content_type_map.get(file_ext, 'application/octet-stream')
        
        # S3 key structure: artifacts/{type}/{artifact_id}/{filename}
        filename = os.path.basename(local_file_path)
        s3_key = f"artifacts/{artifact_type}/{artifact_id}/{filename}"
        
        try:
            # Upload to S3 with PRIVATE access (default)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.upload_file(
                    local_file_path,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'ServerSideEncryption': 'AES256',  # Encrypt at rest
                        'Metadata': {
                            'artifact_id': artifact_id,
                            'artifact_type': artifact_type,
                            'uploaded_at': datetime.utcnow().isoformat()
                        }
                    }
                )
            )
            
            print(f"✅ Uploaded to S3 (private): {s3_key}")
            return s3_key  # Return key, not URL
            
        except ClientError as e:
            print(f"❌ Failed to upload to S3: {e}")
            return None
    
    async def upload_artifact_pair(
        self,
        html_path: str,
        png_path: str,
        artifact_id: str,
        artifact_type: str,
        generate_urls: bool = True,
        url_expiration: int = 86400  # 24 hours default
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Upload both HTML and PNG files for an artifact
        
        Args:
            html_path: Path to HTML file
            png_path: Path to PNG file
            artifact_id: Unique artifact identifier
            artifact_type: Type of artifact
            generate_urls: Generate presigned URLs immediately
            url_expiration: URL expiration time in seconds (default 24 hours)
        
        Returns:
            Tuple of (html_s3_key, png_s3_key) or (html_presigned_url, png_presigned_url) if generate_urls=True
        """
        html_key = await self.upload_artifact(html_path, artifact_id, artifact_type)
        png_key = await self.upload_artifact(png_path, artifact_id, artifact_type)
        
        if generate_urls and html_key and png_key:
            html_url = self.get_presigned_url(html_key, expiration=url_expiration)
            png_url = self.get_presigned_url(png_key, expiration=url_expiration)
            return (html_url, png_url)
        
        return (html_key, png_key)
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for private S3 object
        
        Args:
            s3_key: S3 object key (e.g., 'artifacts/line_chart/abc123/file.html')
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Presigned URL if successful, None otherwise
        
        Example:
            url = s3_service.get_presigned_url('artifacts/line_chart/xyz/chart.html', expiration=86400)
            # URL valid for 24 hours
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"❌ Failed to generate presigned URL: {e}")
            return None
    
    def get_presigned_urls_batch(self, s3_keys: list, expiration: int = 3600) -> Dict[str, Optional[str]]:
        """
        Generate presigned URLs for multiple S3 objects
        
        Args:
            s3_keys: List of S3 object keys
            expiration: URL expiration time in seconds
        
        Returns:
            Dictionary mapping s3_key to presigned URL
        """
        urls = {}
        for key in s3_keys:
            urls[key] = self.get_presigned_url(key, expiration)
        return urls
    
    async def delete_artifact(self, s3_key: str) -> bool:
        """
        Delete artifact from S3
        
        Args:
            s3_key: S3 object key
        
        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
            )
            print(f"✅ Deleted from S3: {s3_key}")
            return True
            
        except ClientError as e:
            print(f"❌ Failed to delete from S3: {e}")
            return False
    
    async def list_artifacts(self, prefix: str = "artifacts/") -> list:
        """
        List artifacts in S3
        
        Args:
            prefix: S3 prefix to filter objects
        
        Returns:
            List of S3 object keys
        """
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except ClientError as e:
            print(f"❌ Failed to list S3 objects: {e}")
            return []


# Global S3 service instance
try:
    s3_service = S3Service()
    print(f"✅ S3 service initialized (bucket: {s3_service.bucket_name})")
except Exception as e:
    print(f"⚠️  S3 service initialization failed: {e}")
    s3_service = None

