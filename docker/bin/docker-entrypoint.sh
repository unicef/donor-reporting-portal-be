#!/bin/sh -e


export MEDIA_ROOT="${MEDIA_ROOT:-/var/run/app/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/run/app/static}"
export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
export DJANGO_SETTINGS_MODULE="donor_reporting_portal.config.settings"

chown -R drp:unicef /app

case "$1" in
    run)
      django-admin upgrade --all
	    set -- tini -- "$@"
	    MAPPING=""
	    if [ "${STATIC_URL}" = "/static/" ]; then
	      MAPPING="--static-map ${STATIC_URL}=${STATIC_ROOT}"
	    fi
      set -- tini -- "$@"
	    set -- uwsgi --http :8000 \
	          -H /venv \
	          --module donor_reporting_portal.config.wsgi \
	          --mimefile=/conf/mime.types \
	          --uid drp \
	          --gid unicef \
            --buffer-size 8192 \
            --http-buffer-size 8192 \
	          $MAPPING
	    ;;
    upgrade)
      django-admin upgrade --all
      ;;
    worker)
      set -- tini -- "$@"
      set -- gosu drp:unicef celery -A donor_reporting_portal.config.celery worker --statedb /app/worker --concurrency=4 -E --loglevel=ERROR
      ;;
    beat)
      set -- tini -- "$@"
      set -- gosu drp:unicef celery -A donor_reporting_portal.config.celery beat --loglevel=ERROR --scheduler django_celery_beat.schedulers:DatabaseScheduler
      ;;
    flower)
      export DATABASE_URL="sqlite://:memory:"
      set -- tini -- "$@"
      set -- gosu drp:unicef celery -A donor_reporting_portal.config.celery flower
      ;;
esac

exec "$@"
