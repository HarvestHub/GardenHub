function gardenhub_db() {
  # Create volume
	docker volume create gardenhub_pgdata
  # Run Postgres
  docker run --rm \
    --name gardenhub_db \
    -v gardenhub_pgdata:/var/lib/postgresql/data \
    -p 54320:5432 \
    -e POSTGRES_PASSWORD=gardenhub \
    -d postgres:10-alpine $@
}

function manage_py() {
  gardenhub_db 2> /dev/null
  until nc -z 0.0.0.0 54320; do
    echo "Postgres is still starting up..."
    sleep 1
  done
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
    -v $(pwd):/app \
    gardenhub python manage.py $@
}

# Build the docker container
function build() {
  echo "Building GardenHub image"
  docker build -t gardenhub .
}

# Run containers
function start() {
  # Build the image if it isn't already
  if ! docker image inspect gardenhub > /dev/null; then
    build
  fi
  manage_py runserver
}

# Stop containers
function stop() {
  docker stop gardenhub_db 2> /dev/null
  docker stop gardenhub 2> /dev/null
  echo "Containers killed"
}

# Restart
function restart() {
  stop
  start
}

# Options
case $1 in
  build) build ;;
  start) start ;;
  stop) stop ;;
  restart) restart ;;
  manage.py)
    shift
    manage_py $@
    ;;
esac
