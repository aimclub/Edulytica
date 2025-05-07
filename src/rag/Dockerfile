FROM python:3.11-slim

WORKDIR /app

COPY src/rag/api_requirements.txt .
COPY src/common/requirements_common.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r api_requirements.txt

ENV PYTHONPATH=/app

COPY . .
COPY src/common /app/src/common

CMD ["uvicorn", "src.rag.app:app", "--host", "0.0.0.0", "--port", "10002"]