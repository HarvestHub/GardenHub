deploy:
	git push dokku master
pull_staging_db:
	scp root@candlewaster.co:/var/lib/dokku/data/storage/gardenhub/db.sqlite3 .
pull_staging_media:
	scp -r root@candlewaster.co:/var/lib/dokku/data/storage/gardenhub/media .
build:
	# Build the image
	docker build -t gardenhub .
devserver:
	pwd | export PWD
	# Quit old containers
	docker rm -f gardenhub gardenhub_db || :
	# Create volume
	docker volume create gardenhub_pgdata
	# Start postgres
	docker run --rm \
		--name gardenhub_db \
		-v gardenhub_pgdata:/var/lib/postgresql/data \
		-p 54320:5432 \
		-e POSTGRES_PASSWORD=gardenhub \
		-d postgres:10-alpine
	# Wait for postgres to start up
	sleep 10
	# Run a container
	docker run --rm \
		--name gardenhub \
		-p 8000:8000 \
		--network=host \
		-e PYTHONUNBUFFERED=0 \
		-e PGHOST=0.0.0.0 \
		-e PGPORT=54320 \
		-e PGUSER=postgres \
		-e PGDATABASE=postgres \
		-e PGPASSWORD=gardenhub \
		-v $(PWD):/app \
		gardenhub \
		python manage.py runserver
