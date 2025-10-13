FROM python:3.13-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY r.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    && pip install --upgrade pip \
    && pip install -r r.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/usr/src/app
COPY . /usr/src/app/