.PHONY: build up down migrate createsuperuser createadmin createdemo setup test shell logs

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

createadmin:
	docker compose exec web python manage.py create_admin

createdemo:
	docker compose exec web python manage.py create_demo

setup: migrate createadmin createdemo
	@echo "✅ Setup complete! Admin and demo users created."

test:
	docker compose run --rm web python manage.py test storage

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f web
