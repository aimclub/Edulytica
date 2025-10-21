#!/bin/sh

set -e

echo "Checking/downloading models for $MODEL_TYPE..."
python3 src/models/download_models.py $MODEL_TYPE
echo "Models are ready. Starting application..."
exec python3 src/models/app.py