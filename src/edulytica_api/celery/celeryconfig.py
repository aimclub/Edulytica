broker_url = "redis://"
result_backend = "redis://"
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Oslo"
broker_connection_retry_on_startup = False
celery_broker_heartbeat = 0
