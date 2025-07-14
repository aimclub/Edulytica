FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/orchestration/requirements.txt .
COPY src/common/requirements_common.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY . .
COPY src/common /app/src/common

COPY src/orchestration/init_kafka.sh /usr/local/bin/init_kafka.sh
RUN chmod +x /usr/local/bin/init_kafka.sh

CMD ["/usr/local/bin/init_kafka.sh"]