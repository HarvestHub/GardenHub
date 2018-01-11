![GardenHub Promo Banner](gardenhub-promo.png)

[![Build Status](https://travis-ci.org/HarvestHub/GardenHub.svg?branch=master)](https://travis-ci.org/HarvestHub/GardenHub)
[![Coverage Status](https://coveralls.io/repos/github/HarvestHub/GardenHub/badge.svg)](https://coveralls.io/github/HarvestHub/GardenHub)
[![Maintainability](https://api.codeclimate.com/v1/badges/831094bb6605cfd9ec68/maintainability)](https://codeclimate.com/github/HarvestHub/GardenHub/maintainability)
[![Known Vulnerabilities](https://snyk.io/test/github/harvesthub/gardenhub/badge.svg)](https://snyk.io/test/github/harvesthub/gardenhub)
[![Requirements Status](https://requires.io/github/HarvestHub/GardenHub/requirements.svg?branch=master)](https://requires.io/github/HarvestHub/GardenHub/requirements/?branch=master)
[![Documentation Status](https://readthedocs.org/projects/gardenhub/badge/?version=latest)](http://gardenhub.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

# GardenHub

Formed around the simple idea that food should not go to waste, GardenHub is the solution to the problem of community garden food waste. Despite the best efforts of community gardeners, far too often food produced in community gardens rots on the vine.

GardenHub is building technology to enable gardeners to collaborate and act upon what's growing, ripening, and available for harvest in their gardens. Using this information, GardenHub notifies gardeners, local charities, restaurants, and other stakeholders of the availability of this food.

[Read the full documentation here.](https://gardenhub.readthedocs.io/en/latest/)

## WIP

GardenHub is a work in progress web application being developed in the open. It's licensed under AGPL-3.0+ and written in Python using the Django framework. You can preview our work on the [demo site](http://gardenhub.candlewaster.co/), but keep in mind that it will change dramatically.

Eventually, the inner-workings of this project will be documented in detail. We're making an effort to self-document the code, so take a look. You're welcome to chat with us by opening a GitHub issue. GardenHub is a project by HarvestHub, and it's being developed by Candlewaster.

## Local development

GardenHub provides a script called `dev.sh` to make local development easy. Its only dependency is [Docker](https://docs.docker.com/engine/installation/). As long as you have Docker installed, you do not need Python, Django, Postgres, or anything else running on your computer for local development with `dev.sh`. This is because `dev.sh` automatically configures a local development environment with Docker containers where all of that is already installed.

**Note:** This has been tested on GNU/Linux. Your mileage may vary using Docker on MacOS or Windows.

To get up and running, [install Docker](https://docs.docker.com/engine/installation/). Next ensure that your user is added to the Docker group (`sudo usermod -aG docker $your_user`; you may need to log out then back in after). Finally, run the following commands:

```
# Clone the repo
git clone https://github.com/HarvestHub/GardenHub.git

# Enter the project folder
cd GardenHub

# Run the local development server
./dev.sh start
```

It may take a few minutes to download everything the first time, then it will run more quickly on subsequent attempts.

`dev.sh` has a few options you can take advantage of.

| Command   | Description                                                                                                           |
|-----------|-----------------------------------------------------------------------------------------------------------------------|
| start     | Launches a Postgres container and a GardenHub app container then starts `manage.py runserver`.                        |
| stop      | Kills and removes all GardenHub containers (database will be preserved).                                              |
| restart   | Same as running `stop` followed by `start`.                                                                           |
| build     | Rebuilds the app container. You must do this **manually** if you change requirements.txt.                             |
| manage.py | Same as running `python manage.py` in the app container. Useful for running migrations and other management commands. |
| setup     | Installs Docker. Works on many GNU/Linux distros.                                                                     |

### Running migrations and management commands

To run migrations, you can use:

```
# Migrate
./dev.sh manage.py migrate

# Make migrations
./dev.sh manage.py makemigrations
```

Any other management command may also be run this way.

### Rebuilding the container (you have to, sometimes)

Changing application code shouldn't require rebuilding the container. However, you must **manually rebuild the container** any time you edit `requirements.txt`. This is because the requirements get installed into the container at build time. You can rebuild the container like so:

```
./dev.sh build
```

## License

GardenHub is copyright © 2017 HarvestHub and licensed under the GNU AGPL version 3 or later. View the `LICENSE` file for a copy of the full license.
