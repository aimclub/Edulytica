FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/auth/requirements.txt .
COPY src/common/requirements_common.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY . .
COPY src/common /app/src/common

CMD ["python","-m","src.auth.app"]