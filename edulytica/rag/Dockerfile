FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY edulytica/rag/requirements.txt .
COPY edulytica/common/requirements_common.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY . .
COPY edulytica/common /app/edulytica/common

CMD ["uvicorn", "edulytica.rag.app:app", "--host", "0.0.0.0", "--port", "15002"]