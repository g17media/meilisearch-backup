# Meilisearch

Meilisearch is a RESTful search API

- https://www.meilisearch.com/
- https://github.com/meilisearch/meilisearch

## Meilisearch-backup

Simple script to backup dump file on s3 storage

Feature:
- containerized
- automatic scheduled
- easy restore dump file
- use in docker-compose or k8s sidecar or k8s cronjob
- save the latest 3 versions by default
- customizable

This is a python container running in docker-compose or cronjob next to **meilisearch**
Containers share a common `/tmp/dumps` directory

### Backup

Backup is done automatically every day in `MEILI_BACKUP_TIME` or you can run `python meilisearch_backup/action/backup.py` manually when connecting to the container

S3 stores the 3 latest versions, you can change the variable `s3_number_of_buckets`

### Restore (only manual)

you can run `python meilisearch_backup/action/restore.py` manually when connecting to the container

```bash
docker-compose exec meilisearch-backup bash
python restore.py
```

In the meilisearch container, make sure the dump is downloaded `/tmp/dumps/meilisearch_backup.dump`

To restore, delete the current data and restart

```bash
docker-compose exec meilisearch sh
rm -rf data.ms
reboot
```

### Dev/Test docker-compose

`docker-compose.yaml` is used for develop and test local, 

Build

```bash
task build
```

Run docker-compose
```bash
task up
```

You need to fill in some data in the **meilisearch** database to check it. Because the minimum size of the dump file = 500Kb

you can use the `test` directory to add data

Run backup
```bash
task run-backup
```

You can check in S3 minio gui that the dump file is loaded `http://localhost:9001`

### Settings

All script settings can be found in the file - `meilisearch_backup/meilisearch_backup/settings.py`


| Variables | Default | Descriptions |
|----------|----------|----------|
| meili_url | http://meilisearch:7700  |  Meilisearch url |
| meili_master_key | DEVLOCALMASTERKEY | Meilisearch MASTER KEY |
| meili_dump_dir | /tmp/dumps | dumps dir |
| meili_backup_time | 01:00:00 | Every day at this time does a dump |
| meili_max_dump_create_time_sec | 3600 | Maximum time for dump task execution |
| meili_min_dump_size_bytes | 500000 | 500kb Minimum dump file size (for protection in case of data loss to avoid overwriting current dump files) |
| s3_backup | True | To disable sending to S3 (will only create dump in local filesystem) |
| s3_endpoint | http://minio:9000| S3 url |
| s3_access_key | minioadmin | S3 access key |
| s3_secret_key | minioadmin | S3 secret key |
| s3_meilisearch_bucket | meilisearch-backup | S3 bucket name |
| s3_backup_name | meilisearch_backup.dump | recovery dump file name |
| s3_number_of_saved_buckets | 3 | number of files to be saved S3 |
| number_of_saved_dumps | 3 | number of files to be saved in the local file system |

---

k8s sidecar container example:
```YAML
containers: 
  - name: meilisearch-backup
    image: meilisearch-backup:1.1.0
    command:
      - python
    args:
      - '-m'
      - meilisearch_backup
    resources:
      limits:
        cpu: 200m
        memory: 256Mi
      requests:
        cpu: 100m
        memory: 128Mi
    envFrom:
      - configMapRef:
          name: meilisearch-environment
    volumeMounts:
      - name: tmp
        mountPath: /tmp
```

k8s cronjob container example:
```
containers: 
  - name: meilisearch-backup
    image: meilisearch-backup:1.1.0
    command:
      - python
    args:
      - 'meilisearch_backup/action/backup.py'
    resources:
      limits:
        cpu: 200m
        memory: 256Mi
      requests:
        cpu: 100m
        memory: 128Mi
    envFrom:
      - configMapRef:
          name: meilisearch-environment
    volumeMounts:
      - name: tmp
        mountPath: /tmp
```
