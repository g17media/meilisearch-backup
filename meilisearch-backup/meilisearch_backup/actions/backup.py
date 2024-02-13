import datetime
import os
import sys
import time
from pathlib import Path

import boto3
from loguru import logger
from meilisearch_python_sdk import Client

sys.path.append(os.getcwd())
from meilisearch_backup.settings import settings


def meilisearch_connect() -> Client:
    meilisearch_client: Client = Client(settings.meili_url, settings.meili_master_key)
    try:
        health: Client.health = meilisearch_client.health()
        meilisearch_client.get_indexes()  # Check MASTER_KEY when connecting
        logger.info(f"Meilisearch {settings.meili_url} {health}")
    except Exception as e:
        logger.error(f"Meilisearch connection error: {e}")
        sys.exit(1)
    return meilisearch_client


def s3_connect() -> boto3.client:
    s3_client: boto3.client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    try:
        s3_client.list_objects(Bucket=settings.s3_meilisearch_bucket)  # Check s3 bucket
        logger.info(f"S3 bucket {settings.s3_meilisearch_bucket} status='available'")
    except Exception as e:
        logger.error(f"S3 connection error: {e}")
        sys.exit(1)
    return s3_client


def create_dump_file() -> str:
    dump_time: int = 0
    client: Client = meilisearch_connect()
    try:
        start_dump: Client.TaskInfo = client.create_dump()
        logger.info(f"Start dump: {start_dump}")
    except Exception as e:
        logger.error(f"Meilisearch error create dump: {e}")
        sys.exit(1)
    result_dump: Client.TaskResult = client.get_task(start_dump.task_uid)
    while result_dump.status != "succeeded" and dump_time <= settings.meili_max_dump_create_time_sec:
        time.sleep(5)
        result_dump = client.get_task(start_dump.task_uid)
        if result_dump.started_at is None:
            logger.info(f"Waiting dump, status: {result_dump.status}")
            dump_time += 5
            continue
        current_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        dump_time = (current_time - result_dump.started_at).total_seconds()
        logger.info(f"Waiting dump, status: {result_dump.status} duration: {dump_time} seconds")
    if result_dump.status != "succeeded":
        logger.error(f"Error dump status: {result_dump.status} dump_time: {dump_time}")
        sys.exit(1)
    file_name: str = result_dump.details["dumpUid"] + ".dump"
    logger.info(f"Dump {result_dump.status}, file_name: {file_name}, duration={result_dump.duration}")
    return file_name


def upload_file_s3(file: str) -> None:
    s3_client: boto3.client.S3 = s3_connect()
    backet_objects = s3_client.list_objects(Bucket=settings.s3_meilisearch_bucket)
    file_path: Path = Path(settings.meili_dump_dir) / file
    logger.info(f"Start upload {file_path} to S3 Minio")
    if not os.path.isfile(file_path):
        logger.error(f"Dump file not found in {file_path}")
        sys.exit(1)
    dump_size: int = os.stat(file_path).st_size
    if dump_size < settings.meili_min_dump_size_bytes:
        logger.error(f"Error minimal dump size {file_path} size={dump_size}bytes")
        sys.exit(1)
    start_upload_time: float = time.time()
    with Path.open(file_path, "rb") as file_object:
        s3_client.upload_fileobj(file_object, settings.s3_meilisearch_bucket, file)
    end_upload_time: float = time.time()
    logger.info(f"S3 upload done, upload time {end_upload_time - start_upload_time} seconds")
    # Clean outdated files S3
    backet_objects = s3_client.list_objects(Bucket=settings.s3_meilisearch_bucket)  # Update connect objects
    s3_sorted_objects = sorted(backet_objects["Contents"], key=lambda obj: obj["LastModified"], reverse=True)
    s3_files_to_delete = s3_sorted_objects[settings.s3_number_of_saved_buckets :]
    for obj in s3_files_to_delete:
        s3_file_name = obj["Key"]
        logger.info(f"Delete outdated file: {s3_file_name}")
        s3_client.delete_object(Bucket=settings.s3_meilisearch_bucket, Key=obj["Key"])


def clean_outdate_dump_file() -> None:
    file_path: Path = Path(settings.meili_dump_dir)
    files: list = os.listdir(file_path)
    files.sort(reverse=True)
    files_to_delete: list = files[settings.number_of_saved_dumps :]
    for obj in files_to_delete:
        logger.info(f"Delete outdated dump file: {obj}")
        try:
            os.remove(f"{file_path}/{obj}")
        except OSError:
            logger.error("Error clean dump file")
            sys.exit(1)


def start_backup() -> None:
    dump_file: str = create_dump_file()
    if settings.s3_backup:
        upload_file_s3(dump_file)
    else:
        logger.info("S3 backup skip. Change settings for enalbe")
    clean_outdate_dump_file()
    logger.info("All jobe done - success backup")


if __name__ == "__main__":
    start_backup()
