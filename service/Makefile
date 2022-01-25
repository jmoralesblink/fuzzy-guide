# RUNNING THE SERVICE

# run the built-in Django development server
runserver:
	poetry run python manage.py runserver 0.0.0.0:8033

# starts db and redis
docker_up:
	docker-compose up -d

# run GUnicorn, in a prod-ready setup
# the actual prod configuration is defined in docker-entrypoint.sh
gunicorn:
	poetry run gunicorn --name="django-service-bootstrap" --error-logfile="-" --bind=":8033" --workers="1" --threads="2" --reload "django_service_bootstrap.wsgi"


# DATABASE

# run database migrations for all apps
run_migrations:
	poetry run python manage.py migrate

# creates migrations if models were updated
build_migrations:
	poetry run python manage.py makemigrations

# resets the database, clears migrations and runs migrations
reset_db:
	poetry run python manage.py reset_service_db "$(shell whoami)@blinkhealth.com"


# TESTING

# runs all unit tests
# copying the line, and replacing the . with a path will run just the tests in that path
#   Ex: poetry run pytest -n 2 --tb=short core.services  # just run service tests
#   Ex: poetry run pytest -n 2 --tb=short core/services/tests/test_foo_service.py  # just run tests in the file
# removing '-n 2' will run tests single-threaded, sometimes showing extra log output, and allow pdb debugging to work
test:
	poetry run pytest -n 2 --tb=short .  # --tb shows a shorter, easier to read, traceback

# runs all unit tests, but will re-create the test db.  useful after model changes
test_update_db:
	poetry run pytest -n 2 --tb=short . --create-db


# MANAGING CODE

# format all Python files (120 matches the line-width guide in PyCharm)
lint:
	poetry run black --line-length 120 .

clean:
	coverage erase
	rm -rfv `find . -type d -name __pycache__`


# MANAGING DEPENDENCIES

# install the exact versions of dependencies that match what is specified in poetry.lock
sync_dependencies:
	poetry install

# update poetry.lock with the latest dependency versions that match what is in pyproject.toml, and install them
update_dependencies:
	poetry update


# LOCAL DEVELOPMENT

# run the ops_tool
ops_tool:
	poetry run python manage.py ops_tool

# run your personal management command
personal:
	poetry run python manage.py personal

# KUBERNETES

prod_context:
	export AWS_PROFILE=django-service-bootstrap-prod
	kubectl config set-context django-service-bootstrap-prod

staging_context:
	export AWS_PROFILE=django-service-bootstrap-staging
	kubectl config set-context django-service-bootstrap-staging

dev_context:
	export AWS_PROFILE=django-service-bootstrap-dev
	kubectl config set-context django-service-bootstrap-dev
