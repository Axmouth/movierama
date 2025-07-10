docker compose -f docker-compose.dev.yml up --build -d

poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8000
