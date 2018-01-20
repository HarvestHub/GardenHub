app="gardenhub"

# Build the docker container
function build() {
  echo "Building $app image"
  docker build -t $app .
}

# Test whether the database is up
function test_db() {
  docker run --rm --network=host \
    -e PGPASSWORD=$app \
    postgres:10-alpine \
    sh -c 'psql -h "0.0.0.0" -p '$db_port' -U "postgres" -c "\q"' &> /dev/null
}

# Start database container
function start_db() {
  # Create volume
  docker volume create ${app}_pgdata
  # Run Postgres
  docker run --rm \
    --name ${app}_db \
    -v ${app}_pgdata:/var/lib/postgresql/data \
    -p 0:5432 \
    -e POSTGRES_PASSWORD=$app \
    -d postgres:10-alpine $@
  # Get DB port
  regex="5432\/tcp -> 0\.0\.0\.0:([0-9]+)"
  if [[ $(docker port ${app}_db) =~ $regex ]]
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
  docker stop ${app}_db 2> /dev/null
}

function manage_py() {
  # Build the image if it isn't already
  if ! docker image inspect $app > /dev/null; then
    build
  fi
  # Start Postgres first if it isn't
  start_db 2> /dev/null
  # Run the app container
  docker run --rm -it \
    -p 8000:8000 \
    --network=host \
    -e PYTHONUNBUFFERED=0 \
    -e DATABASE_URL="postgres://postgres:${app}@0.0.0.0:${db_port}/postgres" \
    -v $(pwd):/app \
    $app python manage.py $@
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
  docker volume rm ${app}_pgdata
  docker volume create ${app}_pgdata
  ssh dokku@candlewaster.co postgres:export $app > db.dump
  start_db
  docker cp db.dump ${app}_db:/db.dump
  docker exec -it ${app}_db sh -c \
    "pg_restore -U postgres -d postgres /db.dump && rm /db.dump"
  echo "Successfully restored staging database!"
}

# Pull media files from staging
function pullmedia() {
  mkdir -p media
  scp -r root@candlewaster.co:/var/lib/dokku/data/storage/${app}/media/* media
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
    echo "$app local development script"
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
