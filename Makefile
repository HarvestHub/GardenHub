
deploy:
	git push dokku master
pull_dev_db:
	scp root@candlewaster.co:/var/lib/dokku/data/storage/gardenhub/db.sqlite3 .
local_prod_test:
	pwd | export PWD
	docker build -t gardenhub .
	docker run -p 127.0.0.1:5000:5000 -v $(PWD)/db.sqlite3:/app/db.sqlite3 -e DJANGO_SETTINGS_MODULE=settings.production -e ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 -e SECRET_KEY=unsecret gardenhub
devserver:
	pwd | export PWD
	docker build -t gardenhub .
	docker run -p 127.0.0.1:5000:5000 -v $(PWD):/app gardenhub python manage.py runserver 0.0.0.0:5000
