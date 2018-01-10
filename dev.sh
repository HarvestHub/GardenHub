# Build the docker container
function build() {
  echo "Building GardenHub image"
  docker build -t gardenhub .
}

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
  # Build the image if it isn't already
  if ! docker image inspect gardenhub > /dev/null; then
    build
  fi
  # Start Postgres first if it isn't
  gardenhub_db 2> /dev/null
  until nc -z 0.0.0.0 54320; do
    echo "Postgres is still starting up..."
    sleep 1
  done
  # Run the app container
  docker run --rm \
    --name gardenhub \
    -p 8000:8000 \
    --network=host \
    -e PYTHONUNBUFFERED=0 \
    -e DATABASE_URL="postgres://postgres:gardenhub@0.0.0.0:54320/postgres" \
    -v $(pwd):/app \
    gardenhub python manage.py $@
}

# Run containers
function start() {
  manage_py runserver
}

# Stop containers
function stop() {
  docker stop gardenhub_db 2> /dev/null
  docker stop gardenhub 2> /dev/null
  echo "Containers killed"
}

# Options
case $1 in
  setup)
    wget -nv -O - https://get.docker.com/ | sh
    ;;
  build) build ;;
  start) start ;;
  stop) stop ;;
  restart) stop && start ;;
  manage.py)
    shift
    manage_py $@
    ;;
  *)
    echo "GardenHub local development script"
    echo ""
    echo "usage: ./dev.sh <command> [<args>]"
    echo ""
    echo "Commands:"
    echo "    setup      Installs Docker."
    echo "    start      Run the app and database containers."
    echo "    stop       Kill app and database containers."
    echo "    restart    Same as stop && start."
    echo "    build      Build the app container."
    echo "    manage.py  Runs python manage.py <args> in the app container."
esac
