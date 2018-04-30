set -e

# Run containers
function start() {
  docker-compose run --rm web python manage.py migrate
  docker-compose up
}

# Pull database from staging to local
function pulldb() {
  ssh dokku@candlewaster.co postgres:export gardenhub > db.dump
  docker-compose down -v
  docker-compose up -d
  docker-compose run --rm -v $(pwd)/db.dump:/db.dump db sh -c \
    "pg_restore -U postgres -h db -d postgres /db.dump"
  docker-compose down
  echo "Successfully restored staging database!"
}

# Pull media files from staging
function pullmedia() {
  mkdir -p media
  ssh gardenhub@candlewaster.co s3cmd get s3://gardenhub/gardenhub --recursive --skip-existing
  rsync -av gardenhub@candlewaster.co:~/gardenhub/ ./media
  ssh gardenhub@candlewaster.co rm -r gardenhub
}

# Serve docs
function servedocs() {
  docker run --rm -it \
    -p 8000:8000 \
    --network=host \
    -e PYTHONUNBUFFERED=0 \
    -v $(pwd):/app \
    $app sh -c "cd /app/docs && sphinx-autobuild -b html . _build/html"
}

# Options
case $1 in
  setup)
    sudo sh -c "wget -nv -O - https://get.docker.com/ | sh"
    ;;
  build) docker-compose build ;;
  start) start ;;
  manage.py)
    shift
    docker-compose run --rm web python manage.py $@
    ;;
  docs) servedocs ;;
  pulldb) pulldb ;;
  pullmedia) pullmedia ;;
  *)
    echo "$app local development script"
    echo ""
    echo "usage: ./dev.sh <command> [<args>]"
    echo ""
    echo "Commands:"
    echo "    start      Run the app for local development on port 5000."
    echo "    build      Manually (re)build the app container."
    echo "    manage.py  Runs python manage.py <args> in the app container."
    echo "    setup      Installs Docker."
    echo "    docs       Runs a local server for the docs on port 5000."
    echo ""
    echo "Staging sync (permission required):"
    echo "    pulldb     Downloads db from staging."
    echo "    pullmedia  Downloads media files from staging."
esac
