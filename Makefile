.PHONY: build up down migrate createsuperuser createdemo test shell logs

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

createsuperuser:
	docker compose exec web python manage.py createsuperuser

createdemo:
	docker compose exec web python manage.py create_demo

test:
	docker compose run --rm web python manage.py test storage

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f web
