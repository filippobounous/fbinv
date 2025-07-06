# Use a patch-specific Python image which receives regular security updates
FROM python:3.11.4-slim

# Install security updates and Python dependencies
WORKDIR /app

RUN apt-get update \
    && apt-get dist-upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e . \
    && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

USER appuser

CMD ["uvicorn", "api.investment.main:app", "--host", "0.0.0.0", "--port", "8000"]
