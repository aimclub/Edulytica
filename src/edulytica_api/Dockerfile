FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc libpq-dev postgresql-client

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . ./src/

#COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
#RUN chmod +x /usr/local/bin/docker-entrypoint.sh
#ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
