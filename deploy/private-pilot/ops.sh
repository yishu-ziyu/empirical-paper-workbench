#!/bin/sh
# All configuration is read from an owner-only file OUTSIDE the checkout.
set -eu
: "${PILOT_ENV_FILE:?absolute private environment file required}"
case "$PILOT_ENV_FILE" in /*) ;; *) echo 'Use an absolute environment file' >&2; exit 2;; esac
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"
python3 - "$PILOT_ENV_FILE" "$ROOT" <<'PYENV'
from pathlib import Path
import stat, sys
p, root = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
if p.is_relative_to(root) or not p.is_file() or stat.S_IMODE(p.stat().st_mode) != 0o600:
    raise SystemExit("Configuration must be a 0600 file outside the checkout")
PYENV
compose() { docker compose --env-file "$PILOT_ENV_FILE" -p "${PILOT_PROJECT:-econpaper-private-pilot}" -f docker-compose.yml -f deploy/private-pilot/compose.yml "$@"; }
case "${1:-}" in
  check) compose config --quiet ;;
  build) test -z "$(git status --porcelain)" || { echo 'Build requires a clean checkout' >&2; exit 2; }; compose build ;;
  up) compose up -d --wait --wait-timeout 180 --force-recreate backend runner frontend gateway ;;
  stop) compose stop ;;
  rebuild) compose up -d --wait --wait-timeout 180 --force-recreate --no-build backend runner frontend gateway ;;
  check-data) compose exec -T backend python scripts/check_card_package.py ;;
  backup)
    : "${PILOT_BACKUP_DIR:?new absolute backup directory required}"
    case "$PILOT_BACKUP_DIR" in /*) ;; *) exit 2;; esac
    test ! -e "$PILOT_BACKUP_DIR" || { echo 'Refusing to overwrite backup' >&2; exit 2; }
    umask 077; mkdir -p "$PILOT_BACKUP_DIR"
    # Freeze all application writers; DB dump and MinIO/files now share a window.
    compose stop gateway frontend runner backend minio
    compose exec -T postgres pg_dump -U econpaper -d econpaper -Fc > "$PILOT_BACKUP_DIR/database.dump"
    compose run --rm --no-deps -T --entrypoint sh backend -c 'tar -C /data -cf - uploads runs sessions' > "$PILOT_BACKUP_DIR/files.tar"
    compose run --rm --no-deps -T archive -C /objects -cf - . > "$PILOT_BACKUP_DIR/objects.tar"
    git rev-parse HEAD > "$PILOT_BACKUP_DIR/checkout-source-sha.txt"
    compose images --format json > "$PILOT_BACKUP_DIR/images.json"
    echo 'Backup written; services remain stopped. Resume with ops.sh up.'
    ;;
  restore)
    : "${PILOT_BACKUP_DIR:?backup directory required}"
    case "${PILOT_PROJECT:-}" in econpaper-private-pilot-restore-*) ;; *) echo 'Restore requires a NEW econpaper-private-pilot-restore-* project' >&2; exit 2;; esac
    test -z "$(compose ps -aq)" || { echo 'Refusing to restore over existing containers' >&2; exit 2; }
    # Also reject retained volumes from a previous project with this name.
    test -z "$(docker volume ls -q --filter "label=com.docker.compose.project=$PILOT_PROJECT")" || { echo 'Refusing existing restore volumes' >&2; exit 2; }
    compose up -d --wait postgres
    compose exec -T postgres pg_restore -U econpaper -d econpaper --no-owner --exit-on-error < "$PILOT_BACKUP_DIR/database.dump"
    compose run --rm --no-deps -T --entrypoint sh backend -c 'tar -C /data -xf -' < "$PILOT_BACKUP_DIR/files.tar"
    compose run --rm --no-deps -T archive -C /objects -xf - < "$PILOT_BACKUP_DIR/objects.tar"
    echo 'Restored into isolated volumes; run ops.sh up and verify in browser.'
    ;;
  *) echo 'Usage: ops.sh check|build|up|stop|rebuild|check-data|backup|restore' >&2; exit 2 ;;
esac
