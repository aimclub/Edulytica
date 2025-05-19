FROM python:3.11-slim

WORKDIR /app

COPY src/models/requirements.txt .
COPY src/common/requirements_common.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY . .
COPY src/common /app/src/common

CMD ["python", "src/models/kafka_worker.py"]