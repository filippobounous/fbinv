FROM python:3.11-slim-bullseye

# Install security updates and Python dependencies
WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.investment.main:app", "--host", "0.0.0.0", "--port", "8000"]
