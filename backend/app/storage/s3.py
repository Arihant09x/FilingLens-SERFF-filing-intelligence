from app.core.config import get_settings


class S3Storage:
	"""S3-compatible storage adapter; boto3 is loaded only when this backend is selected."""

	def __init__(self) -> None:
		settings = get_settings()
		try:
			import boto3
		except ImportError as error:
			raise RuntimeError("Install boto3 to use STORAGE_BACKEND=s3") from error
		self.bucket = getattr(settings, "s3_bucket", "")
		self.client = boto3.client(
			"s3",
			endpoint_url=getattr(settings, "s3_endpoint", None) or None,
			aws_access_key_id=getattr(settings, "s3_access_key", None),
			aws_secret_access_key=getattr(settings, "s3_secret_key", None),
		)

	async def save(self, key: str, content: bytes) -> str:
		self.client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType="application/pdf")
		return key

	async def read(self, key: str) -> bytes:
		return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

	async def delete(self, key: str) -> None:
		self.client.delete_object(Bucket=self.bucket, Key=key)
