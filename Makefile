deploy:
	git push dokku master
	ssh dokku@candlewaster.co run gardenhub python manage.py collectstatic --noinput
pull_dev_db:
	scp root@candlewaster.co:/var/lib/dokku/data/storage/gardenhub/db.sqlite3 .
