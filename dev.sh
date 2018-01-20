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
    sh -c 'psql -h "0.0.0.0" -p '$db_port' -U "postgres" -c "\q"' &> /dev/null
}

# Start database container
function start_db() {
  # Create volume
  docker volume create gardenhub_pgdata
  # Run Postgres
  docker run --rm \
    --name gardenhub_db \
    -v gardenhub_pgdata:/var/lib/postgresql/data \
    -p 0:5432 \
    -e POSTGRES_PASSWORD=gardenhub \
    -d postgres:10-alpine $@
  # Get DB port
  regex="5432\/tcp -> 0\.0\.0\.0:([0-9]+)"
  if [[ $(docker port gardenhub_db) =~ $regex ]]
  then
      db_port="${BASH_REMATCH[1]}"
      echo "Database is listening at port ${db_port}"
  fi
  # Wait for db before continuing
  until test_db -eq 0; do
    echo "Postgres is still starting up..."
    sleep 1
  done
}

# Stop the database container
function stop_db() {
  docker stop gardenhub_db 2> /dev/null
}

function manage_py() {
  # Build the image if it isn't already
  if ! docker image inspect gardenhub > /dev/null; then
    build
  fi
  # Start Postgres first if it isn't
  start_db 2> /dev/null
  # Run the app container
  docker run --rm -it \
    -p 8000:8000 \
    --network=host \
    -e PYTHONUNBUFFERED=0 \
    -e DATABASE_URL="postgres://postgres:gardenhub@0.0.0.0:${db_port}/postgres" \
    -v $(pwd):/app \
    gardenhub python manage.py $@
  # Stop the database when the development server stops
  if [ $1 = "runserver" ]; then
    stop_db
  fi
}

# Run containers
function start() {
  manage_py migrate
  manage_py runserver
}

# Pull database from staging to local
function pulldb() {
  stop
  docker volume rm gardenhub_pgdata
  docker volume create gardenhub_pgdata
  ssh dokku@candlewaster.co postgres:export gardenhub > db.dump
  start_db
  docker cp db.dump gardenhub_db:/db.dump
  docker exec -it gardenhub_db sh -c \
    "pg_restore -U postgres -d postgres /db.dump && rm /db.dump"
  echo "Successfully restored staging database!"
}

# Pull media files from staging
function pullmedia() {
  mkdir -p media
  scp -r root@candlewaster.co:/var/lib/dokku/data/storage/gardenhub/media/* media
}

# Options
case $1 in
  setup)
    sudo sh -c "wget -nv -O - https://get.docker.com/ | sh"
    ;;
  build) build ;;
  start) start ;;
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
    echo "    start      Run the app for local development on port 8000."
    echo "    build      Manually (re)build the app container."
    echo "    manage.py  Runs python manage.py <args> in the app container."
    echo "    setup      Installs Docker."
    echo ""
    echo "Staging sync (permission required):"
    echo "    pulldb     Downloads db from staging."
    echo "    pullmedia  Downloads media files from staging."
esac
