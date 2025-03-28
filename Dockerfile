FROM python:3.11-slim AS base
FROM mcr.microsoft.com/playwright/python:v1.51.0-noble

WORKDIR /code

COPY setup.txt /code/setup.txt

RUN apt-get update && apt-get install -y curl && \
    pip install --no-cache-dir --upgrade -r /code/setup.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /code

RUN playwright install --with-deps

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8088"]
