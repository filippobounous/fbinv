FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pip --upgrade \
    && pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.investment.main:app", "--host", "0.0.0.0", "--port", "8000"]
