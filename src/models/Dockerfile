FROM python:3.11-slim

WORKDIR /app

COPY src/models/requirements.txt .
COPY src/common/requirements_common.txt .
# COPY src/LLM/requirements_llm.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r requirements.txt
# RUN pip install -r requirements_llm.txt

ENV PYTHONPATH=/app

COPY . .
COPY src/common /app/src/common
COPY src/LLM /app/src/LLM

CMD ["python", "src/models/app.py"]