FROM python:3.13.0-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY r.txt .
RUN pip install -r r.txt
RUN pip install celery

RUN apk update && apk add --no-cache bash curl dcron

COPY cron/backup-cron.sh /app/backup-cron.sh
COPY . /usr/src/app/
