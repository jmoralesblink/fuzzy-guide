#!/usr/bin/env bash
set -ex

STATSD_HOST="dogstatsd.datadog.svc.cluster.local"
>&2 echo "statsd: $STATSD_HOST"

GUNICORN_CMD="gunicorn"
if [ -n "${NEW_RELIC_CONFIG_FILE}" ]; then
  GUNICORN_CMD="newrelic-admin run-program gunicorn"
fi

# restart a worker after processing this many requests, to keep them from getting stale
MAX_REQUESTS=5000

exec ${GUNICORN_CMD} \
  --name="django-service-bootstrap" \
  --statsd-prefix="django_service_bootstrap" \
  --statsd-host="${STATSD_HOST}:8125" \
  --error-logfile="-" \
  --bind=":8000" \
  --workers="3" \
  --threads="4" \
  --max-requests ${MAX_REQUESTS} \
  "django_service_bootstrap.wsgi"
