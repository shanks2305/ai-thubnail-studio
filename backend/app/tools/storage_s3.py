from uuid import uuid4

import boto3

from app.core.config import get_settings


def save_s3(project_id: str, kind: str, data: bytes, suffix: str) -> str:
    bucket = _bucket()
    key = f"{project_id}/{kind}/{uuid4().hex}{suffix}"
    _client().put_object(Bucket=bucket, Key=key, Body=data)
    return f"s3://{bucket}/{key}"


def read_s3(uri: str) -> bytes:
    bucket, key = _split(uri)
    if bucket != _bucket():
        raise ValueError("Asset path is outside storage")
    return _client().get_object(Bucket=bucket, Key=key)["Body"].read()


def delete_s3(uri: str) -> None:
    bucket, key = _split(uri)
    if bucket != _bucket():
        raise ValueError("Asset path is outside storage")
    _client().delete_object(Bucket=bucket, Key=key)


def delete_prefix(project_id: str) -> None:
    client = _client()
    bucket = _bucket()
    listed = client.list_objects_v2(Bucket=bucket, Prefix=f"{project_id}/")
    objects = [{"Key": item["Key"]} for item in listed.get("Contents", [])]
    if objects:
        client.delete_objects(Bucket=bucket, Delete={"Objects": objects})


def _bucket() -> str:
    bucket = get_settings().s3_bucket
    if not bucket:
        raise ValueError("Set S3_BUCKET.")
    return bucket


def _client():
    settings = get_settings()
    kwargs: dict[str, str] = {"region_name": settings.aws_region}
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def _split(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError("Asset path is outside storage")
    bucket, _, key = uri.removeprefix("s3://").partition("/")
    if not bucket or not key:
        raise ValueError("Asset path is outside storage")
    return bucket, key
