import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    meili_url: str = "http://meilisearch:7700"
    meili_master_key: str = "DEVLOCALMASTERKEY"
    meili_dump_dir: str = "/tmp/dumps"
    meili_backup_time: str = "01:00:00"
    meili_max_dump_create_time_sec: int = 3600  # 60 min
    meili_min_dump_size_bytes: int = 500000  # 500Kb
    s3_backup: bool = True  # Change the value to False to save only to disk
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_meilisearch_bucket: str = "meilisearch-backup"
    s3_backup_name: str = "meilisearch_backup.dump"
    s3_number_of_saved_buckets: int = 3  # save latest files by date S3
    number_of_saved_dumps: int = 3  # save latest files by date (meilisearch dump dir)


settings: Settings = Settings()
