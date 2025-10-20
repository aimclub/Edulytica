FROM nvidia/cuda:12.9.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/common/requirements_common.txt .
RUN pip3 install -r requirements_common.txt

COPY src/models/requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=/app

COPY src/common /app/src/common
COPY src/models /app/src/models

ARG MODEL_TYPE
RUN python3 src/models/download_models.py $MODEL_TYPE

ENV MODEL_TYPE=$MODEL_TYPE

CMD ["python3", "src/models/app.py"]