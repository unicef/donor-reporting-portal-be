# envs to set before use this script
DATABASE_URL?=
DOCKER_PASS?=
DOCKER_USER?=
TARGET?=1.6.0
BASE?=$(shell echo "${TARGET}" | sed "s/\([0-9]\)\.\([0-9]\)\.\(.*\)/\1.\2/g" )
# below vars are used internally
BUILD_OPTIONS?=
CMD?=donor_reporting_portal
CONTAINER_NAME?=donor_reporting_portal-${TARGET}
ORGANIZATION=unicef
IMAGE_NAME=donor-reporting-portal-backend
DOCKER_IMAGE_NAME?=${ORGANIZATION}/${IMAGE_NAME}
DOCKER_IMAGE?=${DOCKER_IMAGE_NAME}:${TARGET}
DOCKERFILE?=Dockerfile
RUN_OPTIONS?=
PORTS=
ABSOLUTE_BASE_URL?="http://192.168.66.66:8000"

help:
	@echo "dev                  build dev image (based on local code)"
	@echo "build                build production image (based on tag ${TARGET})"
	@echo "release              release tag ${TARGET} on docker hub"
	@echo "run                  run ${DOCKER_IMAGE} locally"


info:
	@echo 'docker images'
	@docker images | grep donor-reporting-portal
	@echo '------------------'
	@echo 'docker containers'
	@docker ps -a | grep donor-reporting-portal


build-base:
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--no-cache \
			-t ${DOCKER_IMAGE_NAME}:${BASE}-base \
			-f docker/Dockerfile.base .
	@echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
	docker push ${DOCKER_IMAGE_NAME}:${BASE}-base


.build:
#	cd .. && ./manage.py makemigrations --check --dry-run
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--build-arg BASE_IMAGE=${BASE} \
			--build-arg VERSION=${TARGET} \
			-t ${DOCKER_IMAGE} \
			-f docker/Dockerfile .
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:dev
	docker images | grep ${DOCKER_IMAGE_NAME}

build-test:
	TARGET=dev $(MAKE) .build test

build:
	$(MAKE) .build test

.run:
	cd .. && docker run \
	 		--rm \
			-e ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
			-e CACHE_URL=redis://192.168.66.66:6379/1 \
			-e CACHE_URL_API=redis://192.168.66.66:6379/2 \
			-e CACHE_URL_LOCK=redis://192.168.66.66:6379/3 \
			-e CACHE_URL_TEMPLATE=redis://192.168.66.66:6379/4 \
			-e CELERY_BROKER_URL=redis://192.168.66.66:6379/2 \
			-e CELERY_RESULT_BACKEND=redis://192.168.66.66:6379/3 \
			-e CSRF_COOKIE_SECURE=false \
			-e DATABASE_URL=${DATABASE_URL} \
			-e DEBUG=false \
			-e DJANGO_SETTINGS_MODULE=donor_reporting_portal.config.settings \
			-e SECURE_BROWSER_XSS_FILTER=0 \
			-e SECURE_CONTENT_TYPE_NOSNIFF=0 \
			-e SECURE_FRAME_DENY=0 \
			-e SECURE_HSTS_SECONDS=0 \
			-e SECURE_HSTS_PRELOAD=false \
			-e SECURE_SSL_REDIRECT=false \
			-e SESSION_COOKIE_HTTPONLY=false \
			-e SESSION_COOKIE_SECURE=false \
			-e STATIC_ROOT=/var/donor_reporting_portal/static/ \
			-e DEVELOPMENT_MODE=0 \
			-e X_FRAME_OPTIONS="SAMEORIGIN" \
			-e AZURE_CLIENT_ID=${AZURE_CLIENT_ID} \
			-e AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET} \
			-e AZURE_TENANT=${AZURE_TENANT} \
			-e INSIGHT_URL=${INSIGHT_URL} \
			-e SHAREPOINT_USERNAME=${SHAREPOINT_USERNAME} \
			-e SHAREPOINT_PASSWORD=${SHAREPOINT_PASSWORD} \
			${RUN_OPTIONS} \
			${DOCKER_IMAGE} \
			${CMD}

local:
	RUN_OPTIONS="-v ${PWD}/..:/code -e PYTHONPATH=/code -it" \
	CMD="/bin/bash" \
	$(MAKE) .run

release:
	@echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
	docker tag ${DOCKER_IMAGE_NAME}:${TARGET} ${DOCKER_IMAGE_NAME}:dev
	docker push ${DOCKER_IMAGE_NAME}:${TARGET}
	docker push ${DOCKER_IMAGE_NAME}:dev

# deploy:
#	lazo rancher upgrade donor_reporting_portal:donor_reporting_portal ${DOCKER_IMAGE_NAME}:${TARGET}
# 	lazo rancher upgrade donor_reporting_portal:celery ${DOCKER_IMAGE_NAME}:${TARGET}
# 	lazo rancher upgrade donor_reporting_portal:beat ${DOCKER_IMAGE_NAME}:${TARGET}
#	lazo rancher upgrade donor_reporting_portal:donor_reporting_portal-admin ${DOCKER_IMAGE_NAME}:${TARGET}
# 	lazo rancher upgrade donor_reporting_portal:celery-w2 ${DOCKER_IMAGE_NAME}:${TARGET}
#	curl -X POST -H 'Content-type: application/json' \
#		--data '{"text":"Donor Reporting Portal ${TARGET} released in dev"}' \
#		https://hooks.slack.com/services/${SLACK_BOT_TOKEN}
#
# staging:
#	echo "="
#
# production:
#	lazo rancher \
#		-b https://elgaucho.unicef.io/v3 \
#		--auth ${RANCHER_GAUCHO_AUTH}
#		upgrade \
#		-c rke-cluster-etdw \
#		-p donor_reporting_portal-prod \
#		--check-image \
#		donor_reporting_portal-prod:donor_reporting_portal ${DOCKER_IMAGE_NAME}:${TARGET}
#
#	curl -X POST -H 'Content-type: application/json' \
#		--data '{"text":"Donor Reporting Portal ${TARGET} released in production"}' \
#		https://hooks.slack.com/services/${SLACK_BOT_TOKEN}

bump:
	cd .. && bumpversion --commit --tag --config-file=.bumpversion.cfg num

run:
	RUN_OPTIONS="-p 8000:8000" \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
		$(MAKE) .run

stack:
	RUN_OPTIONS="-p 8000:8000" \
		CMD=stack \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
		$(MAKE) .run

workers:
	CONTAINER_NAME=donor_reporting_portal-workers \
			ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
			CMD=w2 $(MAKE) .run

beat:
	CONTAINER_NAME=donor_reporting_portal-beat \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
		CMD=beat $(MAKE) .run


test:
	RUN_OPTIONS="-e DEBUG=0 \
				 -e X_FRAME_OPTIONS=DENY \
				 -e SESSION_COOKIE_SECURE=1 \
				 -e CSRF_COOKIE_SECURE=1 \
				 -e SECURE_HSTS_PRELOAD=1 \
				 -e SECURE_SSL_REDIRECT=1" \
	CMD='bash -c "touch /var/donor_reporting_portal/.touch && django-admin check --deploy "' \
	$(MAKE) .run

scratch:
	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

shell:
	RUN_OPTIONS="-p 8000:8000 -it" \
		ABSOLUTE_BASE_URL=${ABSOLUTE_BASE_URL} \
	CMD='/bin/bash' \
		$(MAKE) .run
#	docker exec -it ${CONTAINER_NAME} /bin/bash
#	RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

docker-remove:
	docker-remove.sh ${IMAGE_NAME} -o ${ORGANIZATION}

