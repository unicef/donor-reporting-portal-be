#!/bin/bash -e
mkdir -p /var/donor_reporting_portal/static
mkdir -p /var/donor_reporting_portal/log
mkdir -p /var/donor_reporting_portal/conf
mkdir -p /var/donor_reporting_portal/run

if [[ "$*" == "worker" ]];then
    celery -A donor_reporting_portal.config \
            worker \
            --events \
            --max-tasks-per-child=1 \
            --loglevel=${CELERY_LOGLEVEL} \
            --autoscale=${CELERY_AUTOSCALE} \
            --pidfile run/celery.pid \
            $CELERY_EXTRA


elif [[ "$*" == "beat" ]];then
    celery -A donor_reporting_portal.config beat \
            $CELERY_EXTRA \
            --loglevel=${CELERY_LOGLEVEL} \
            --pidfile run/celerybeat.pid

elif [[ "$*" == "w2" ]];then
    django-admin db_isready --wait --timeout 60

elif [[ "$*" == "donor_reporting_portal" ]];then
    rm -f /var/donor_reporting_portal/run/*

    django-admin diffsettings --output unified

    django-admin db_isready --wait --timeout 60
    django-admin check --deploy
    django-admin upgrade --all --verbosity 2
    django-admin db_isready --wait --timeout 300
    echo "uwsgi --static-map ${STATIC_URL}=${STATIC_ROOT}"
#    exec gosu donor_reporting_portal uwsgi --static-map ${STATIC_URL}=${STATIC_ROOT}
#    newrelic-admin run-program
    uwsgi --static-map ${STATIC_URL}=${STATIC_ROOT}
else
    exec "$@"
fi
