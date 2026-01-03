FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update --allow-releaseinfo-change \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir . \
#    && rm -rf /root/.cache/pip

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
