FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu22.04

WORKDIR /app

COPY src/models/requirements.txt .
COPY src/common/requirements_common.txt .
# COPY src/LLM/requirements_llm.txt .

RUN pip install -r requirements_common.txt
RUN pip install -r requirements.txt
# RUN pip install -r requirements_llm.txt

ENV PYTHONPATH=/app

COPY src/common /app/src/common
COPY src/llm /app/src/llm

CMD ["python", "src/models/app.py"]