FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc libpq-dev postgresql-client

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY . .

COPY src/edulytica_api/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["uvicorn", "src.edulytica_api.app:app", "--host", "0.0.0.0", "--port", "8000"]