import time
from loguru import logger
from schedule import every, repeat, run_pending

from meilisearch_backup.actions import backup
from meilisearch_backup.settings import settings


WHILE_SLEEP_TIME_SEC: int = 60


@repeat(every().day.at(settings.meili_backup_time))
def start_backup_job() -> None:
    logger.info("Start backup job")
    backup.start_backup()


def backup_scheduler() -> None:
    logger.info(f"Run scheduler. Backup time every day at {settings.meili_backup_time}")
    while True:
        run_pending()
        time.sleep(WHILE_SLEEP_TIME_SEC)


def check_settings() -> None:
    logger.info(f"Check connection meilisearch: {settings.meili_url}")
    backup.meilisearch_connect()
    if settings.s3_backup:
        logger.info(f"Check connection S3: {settings.s3_endpoint}")
        backup.s3_connect()


if __name__ == "__main__":
    check_settings()
    backup_scheduler()
