                                #!/usr/bin/env bash
set -e

until kafka-topics --bootstrap-server kafka:9092 --list >/dev/null 2>&1; do
  echo "Waiting for Kafka…"
  sleep 2
done

kafka-topics \
  --bootstrap-server kafka:9092 \
  --create \
  --topic llm_tasks.result \
  --partitions 1 \
  --replication-factor 1 || true

exec uvicorn src.orchestration.main:app \
  --host 0.0.0.0 \
  --port ${ORCHESTRATOR_PORT:-15001}