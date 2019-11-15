#!/bin/bash -e
mkdir -p /var/donor_reporting_portal/static
mkdir -p /var/donor_reporting_portal/log
mkdir -p /var/donor_reporting_portal/conf
mkdir -p /var/donor_reporting_portal/run

chown donor_reporting_portal:donor_reporting_portal -R /var/donor_reporting_portal/


if [[ "$*" == "worker" ]];then
    django-admin db-isready --wait --sleep 5 --timeout 60
    django-admin db-isready --wait --sleep 5 --timeout 300 --connection donor_reporting_portal
    exec gosu donor_reporting_portal celery worker \
            -A donor_reporting_portal \
            --events \
            --max-tasks-per-child=1 \
            --loglevel=${CELERY_LOGLEVEL} \
            --autoscale=${CELERY_AUTOSCALE} \
            --pidfile run/celery.pid \
            $CELERY_EXTRA


elif [[ "$*" == "beat" ]];then
    exec gosu donor_reporting_portal celery beat -A donor_reporting_portal.celery \
            $CELERY_EXTRA \
            --loglevel=${CELERY_LOGLEVEL} \
            --pidfile run/celerybeat.pid

elif [[ "$*" == "w2" ]];then
    django-admin db-isready --wait --timeout 60
    exec gosu donor_reporting_portal circusd /etc/circus.conf --log-output=-

elif [[ "$*" == "donor_reporting_portal" ]];then
    rm -f /var/donor_reporting_portal/run/*

    django-admin diffsettings --output unified
#    django-admin makemigrations --check --dry-run

    django-admin db-isready --wait --timeout 60
    django-admin check --deploy
#    django-admin init-setup --all --verbosity 2
    django-admin db-isready --wait --timeout 300
    echo "uwsgi --static-map ${STATIC_URL}=${STATIC_ROOT}"
    exec gosu donor_reporting_portal uwsgi --static-map ${STATIC_URL}=${STATIC_ROOT}
else
    exec "$@"
fi
