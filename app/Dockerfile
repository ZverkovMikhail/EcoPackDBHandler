FROM python:3.12.2-slim-bookworm

WORKDIR /app

COPY requirements.txt ./
COPY entrypoint.sh /app/entrypoint.sh


RUN apt-get update && apt-get install -y default-mysql-client
RUN pip install --no-cache-dir -r requirements.txt


COPY . .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]