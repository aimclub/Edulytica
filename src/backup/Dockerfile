FROM python:3.11-alpine

RUN apk add --no-cache postgresql16-client tzdata

WORKDIR /app

COPY src/backup/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/backup/backup.py .
COPY ./src/backup/crontab /etc/crontabs/root

RUN mkdir -p /var/log

CMD ["crond", "-f", "-l", "2"]