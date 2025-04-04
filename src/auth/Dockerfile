FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

COPY . .
COPY src/database_module /app/src/database_module

CMD ["uvicorn", "src.auth.app:app", "--host", "0.0.0.0", "--port", "8001"]