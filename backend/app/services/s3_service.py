import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region
        )

    def upload_image(self, image_bytes, object_name):
        """Upload an image to an S3 bucket"""
        if not self.bucket_name:
            logger.warning("AWS_STORAGE_BUCKET_NAME not set. Skipping S3 upload.")
            return None

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_name}"
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return None
