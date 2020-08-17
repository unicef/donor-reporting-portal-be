ARG BASE_IMAGE=1.1.0

FROM unicef/donor-reporting-portal-backend:${BASE_IMAGE}-base

#ARG BUILD_DATE
#ARG VERSION

#ENV GITHUB_TOKEN=${GITHUB_TOKEN}
#ENV DONOR_REPORTING_PORTAL_VERSION=${VERSION}

RUN mkdir -p /code
COPY . /code
WORKDIR /code

RUN set -ex \
    ls -al /code \
    && sha1sum -c /CHECKSUM \
    && pip3 install . \
    && rm -fr /code


LABEL org.label.name="Donor Reporting Portal" \
      org.label.maintainer="ddinicola@unicef.org" \
      org.label.description="" \
      org.label.url="https://donor-reporting-portal.unicef.io/" \
      org.label.vcs-url="https://github.com/unicef/donor-reporting-portal-be"


ENV PIPENV_PYPI_MIRROR=${PIPENV_PYPI_MIRROR}, \
    HOME=/root/ \
    PYTHONUNBUFFERED=1 \
    ALLOWED_HOSTS="*" \
    CACHE_URL="redis://127.0.0.1:6379/1" \
    CELERY_AUTOSCALE="5,1" \
    CELERY_BROKER_URL="redis://127.0.0.1:6379/2" \
    CELERY_LOGLEVEL="ERROR" \
    CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/3" \
    CELERY_EXTRA="" \
    CSRF_COOKIE_SECURE=True \
    DATABASE_URL="postgres://postgres:@192.168.66.66:5432/donor_reporting_portal" \
    DEBUG=0 \
    DJANGO_SETTINGS_MODULE=donor_reporting_portal.config.settings \
    MEDIA_ROOT=/tmp/media \
    SECRET_KEY="secret" \
    SECURE_BROWSER_XSS_FILTER=True \
    SECURE_CONTENT_TYPE_NOSNIFF=True \
    SECURE_FRAME_DENY=True \
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True \
    SECURE_HSTS_PRELOAD=True \
    SECURE_HSTS_SECONDS=1 \
    SECURE_SSL_REDIRECT=True \
    SENTRY_DSN="" \
    SESSION_COOKIE_HTTPONLY=True \
    SESSION_COOKIE_SECURE=True

ENV UWSGI_PROTOCOL=http \
    UWSGI_WORKERS=4 \
    UWSGI_AUTO_PROCNAME=true \
    UWSGI_BUFFER_SIZE=32768 \
    UWSGI_DIE_ON_TERM=true \
    UWSGI_DISABLE_LOGGING=false \
    UWSGI_DISABLE_WRITE_EXCEPTION=true \
    UWSGI_FREEBIND=true \
    UWSGI_HARAKIRI=180 \
    UWSGI_HTTP_TIMEOUT=180 \
    UWSGI_IGNORE_SIGPIPE=true \
    UWSGI_IGNORE_WRITE_ERRORS=true \
    UWSGI_LIMIT_POST=20971520 \
    UWSGI_LOG_X_FORWARDED_FOR=false \
    UWSGI_MEMORY_REPORT=true \
    UWSGI_NEED_APP=true \
    UWSGI_POST_BUFFERING=65536 \
    UWSGI_PROCNAME_PREFIX_SPACED="[DonorReportingPortal]" \
    UWSGI_RELOAD_ON_RSS=600 \
    UWSGI_THREADS=4 \
    UWSGI_THUNDER_LOCK=true \
    UWSGI_VACUUM=true \
    UWSGI_MODULE="donor_reporting_portal.config.wsgi:application" \
    UWSGI_HTTP_SOCKET=0.0.0.0:8000 \
    UWSGI_MASTER=true \
    UWSGI_ENABLE_THREADS=true \
    UWSGI_LAZY_APPS=true \
    UWSGI_SINGLE_INTERPRETER=true

EXPOSE 8000

ADD docker/*.sh /usr/local/bin/

#RUN addgroup --gid 1024 donor_reporting_portal \
#    && adduser --disabled-password --ingroup donor_reporting_portal -S donor_reporting_portal

RUN django-admin collectstatic --noinput

ENTRYPOINT ["entrypoint.sh"]
RUN ["chmod", "+x", "/usr/local/bin/entrypoint.sh"]
WORKDIR /var/donor_reporting_portal

CMD ["donor_reporting_portal"]
