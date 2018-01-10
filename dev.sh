# Build the docker container
function build() {
  echo "Building GardenHub image"
  docker build -t gardenhub .
}

# Test whether the database is up
function test_db() {
  docker run --rm --network=host \
    -e PGPASSWORD=gardenhub \
    postgres:10-alpine \
    sh -c 'psql -h "0.0.0.0" -p 54320 -U "postgres" -c "\q"' &> /dev/null
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
  # Wait for db before continuing
  until test_db -eq 0; do
    echo "Postgres is still starting up..."
    sleep 1
  done
}

function manage_py() {
  # Build the image if it isn't already
  if ! docker image inspect gardenhub > /dev/null; then
    build
  fi
  # Start Postgres first if it isn't
  gardenhub_db 2> /dev/null
  # Run the app container
  docker run --rm -it \
    -p 8000:8000 \
    --network=host \
    -e PYTHONUNBUFFERED=0 \
    -e DATABASE_URL="postgres://postgres:gardenhub@0.0.0.0:54320/postgres" \
    -v $(pwd):/app \
    gardenhub python manage.py $@
}

# Run containers
function start() {
  manage_py migrate
  manage_py runserver
}

# Stop containers
function stop() {
  docker stop gardenhub_db 2> /dev/null
  echo "Database killed"
}

# Pull database from staging to local
function pulldb() {
  stop
  docker volume rm gardenhub_pgdata
  docker volume create gardenhub_pgdata
  ssh dokku@candlewaster.co postgres:export gardenhub > db.dump
  gardenhub_db
  docker cp db.dump gardenhub_db:/db.dump
  docker exec -it gardenhub_db sh -c \
    "pg_restore -U postgres -d postgres /db.dump && rm /db.dump"
}

# Pull media files from staging
function pullmedia() {
  scp -r root@candlewaster.co:/var/lib/dokku/data/storage/gardenhub/media/* media
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
  pulldb) pulldb ;;
  pullmedia) pullmedia ;;
  *)
    echo "GardenHub local development script"
    echo ""
    echo "usage: ./dev.sh <command> [<args>]"
    echo ""
    echo "Commands:"
    echo "    setup      Installs Docker."
    echo "    start      Run the app and database containers."
    echo "    stop       Kill database container."
    echo "    restart    Same as stop && start."
    echo "    build      Build the app container."
    echo "    manage.py  Runs python manage.py <args> in the app container."
    echo ""
    echo "Staging sync (permission required):"
    echo "    pulldb     Downloads db from staging."
    echo "    pullmedia  Downloads media files from staging."
esac
