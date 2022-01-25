FROM python:3.9-slim

ARG ARTIFACTORY_USER
ARG ARTIFACTORY_PASSWORD

ADD poetry.lock pyproject.toml /app/
WORKDIR /app

ENV PATH = "${PATH}:/root/.poetry/bin"

RUN apt-get update -y \
  && apt-get install -y gcc \
  && apt-get install -y curl \
  && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
  | python - \
  && /bin/bash -c "source $HOME/.poetry/env" \
  && poetry check \
  && poetry config virtualenvs.create false \
  && poetry config repositories.blink https://blink.jfrog.io/blink/api/pypi/pypi \
  && poetry config http-basic.blink ${ARTIFACTORY_USER} ${ARTIFACTORY_PASSWORD} \
  && poetry install --no-root --no-dev --no-interaction

COPY . .
