FROM nvidia/cuda:12.9.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY edulytica/models/requirements.txt .
COPY edulytica/common/requirements_common.txt .

RUN pip3 install -r requirements_common.txt
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=/app

COPY edulytica/llm /app/edulytica/llm
COPY edulytica/models/download_models.py .
COPY edulytica/exceptions /app/edulytica/exceptions

ARG MODEL_TYPE
RUN python3 download_models.py $MODEL_TYPE

COPY edulytica/common /app/edulytica/common
COPY edulytica/models/app.py .
COPY edulytica/models/kafka_worker.py .

ENV MODEL_TYPE=$MODEL_TYPE

CMD ["python3", "edulytica/models/app.py"]