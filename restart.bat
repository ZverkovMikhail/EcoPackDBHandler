docker compose down
rmdir dbdata /s /q
docker system prune
docker compose build --no-cache
docker compose up -d