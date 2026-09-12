#!/bin/sh
set -eu
# No xtrace: admin commands receive secrets. Never suppress initialization failure.
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null
mc mb --ignore-existing local/econpaper-uploads >/dev/null
mc admin user add local "$S3_ECONPAPER_USER" "$S3_ECONPAPER_PASSWORD" >/dev/null
printf '%s' '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:PutObject","s3:GetObject","s3:DeleteObject","s3:ListBucket"],"Resource":["arn:aws:s3:::econpaper-uploads","arn:aws:s3:::econpaper-uploads/*"]}]}' > /tmp/policy.json
mc admin policy create local econpaper-app /tmp/policy.json >/dev/null
mc admin policy attach local econpaper-app --user "$S3_ECONPAPER_USER" >/dev/null
mc alias set app http://minio:9000 "$S3_ECONPAPER_USER" "$S3_ECONPAPER_PASSWORD" >/dev/null
printf readiness | mc pipe app/econpaper-uploads/uploads/.readiness >/dev/null
mc cat app/econpaper-uploads/uploads/.readiness >/dev/null
mc rm app/econpaper-uploads/uploads/.readiness >/dev/null
printf 'Bucket and application permissions ready\n'
