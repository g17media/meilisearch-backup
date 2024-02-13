import os
import sys
from pathlib import Path

import boto3
from loguru import logger


sys.path.append(os.getcwd())
from meilisearch_backup.settings import settings


FILE_PATH: Path = Path(settings.meili_dump_dir) / settings.s3_backup_name


def download_file_s3() -> None:
    """For download S3 backup file to dump dir."""
    logger.info("Start download dump S3 Minio")
    s3_client: boto3.client.S3 = boto3.client(
        "s3",
        endpoint_url=settings.platform.s3_endpoint,
        aws_access_key_id=settings.platform.s3_access_key,
        aws_secret_access_key=settings.platform.s3_secret_key,
    )
    try:
        backet_objects = s3_client.list_objects(Bucket=settings.s3_meilisearch_bucket)
    except Exception:
        logger.error("S3 connection error: {e}")
        sys.exit(1)
    s3_sorted_objects = sorted(backet_objects["Contents"], key=lambda obj: obj["LastModified"], reverse=True)
    s3_latest_dump = s3_sorted_objects[0]
    with Path.open(FILE_PATH, "wb") as file:
        s3_client.download_fileobj(settings.s3_meilisearch_bucket, s3_latest_dump["Key"], file)
    logger.info(f"Download file succeded {FILE_PATH}")
    logger.info("To applay dump, need exec meilisearch -> remove current dir: data.ms and restart")


if __name__ == "__main__":
    download_file_s3()
