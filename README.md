![GardenHub Promo Banner](gardenhub-promo.png)

[![Build Status](https://travis-ci.org/HarvestHub/GardenHub.svg?branch=master)](https://travis-ci.org/HarvestHub/GardenHub)
[![Coverage Status](https://coveralls.io/repos/github/HarvestHub/GardenHub/badge.svg)](https://coveralls.io/github/HarvestHub/GardenHub)
[![Maintainability](https://api.codeclimate.com/v1/badges/831094bb6605cfd9ec68/maintainability)](https://codeclimate.com/github/HarvestHub/GardenHub/maintainability)
[![Known Vulnerabilities](https://snyk.io/test/github/harvesthub/gardenhub/badge.svg)](https://snyk.io/test/github/harvesthub/gardenhub)
[![Requirements Status](https://requires.io/github/HarvestHub/GardenHub/requirements.svg?branch=master)](https://requires.io/github/HarvestHub/GardenHub/requirements/?branch=master)
[![License: GPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

# GardenHub

Formed around the simple idea that food should not go to waste, GardenHub is the solution to the problem of community garden food waste. Despite the best efforts of community gardeners, far too often food produced in community gardens rots on the vine.

GardenHub is building technology to enable gardeners to collaborate and act upon what's growing, ripening, and available for harvest in their gardens. Using this information, GardenHub notifies gardeners, local charities, restaurants, and other stakeholders of the availability of this food.

## WIP

GardenHub is a work in progress web application being developed in the open. It's licensed under AGPL-3.0+ and written in Python using the Django framework. You can preview our work on the [demo site](http://gardenhub.candlewaster.co/), but keep in mind that it will change dramatically.

Eventually, the inner-workings of this project will be documented in detail. We're making an effort to self-document the code, so take a look. You're welcome to chat with us by opening a GitHub issue. GardenHub is a project by HarvestHub, and it's being developed by Candlewaster.

## Local development

Developing on GardenHub is easy.

First, install [Docker](https://docs.docker.com/engine/installation/) if you haven't already (you're on your own for that).

Next, run the following commands.

```
# Clone the repo
git clone https://github.com/HarvestHub/GardenHub.git

# Enter the project folder
cd GardenHub

# Build the Docker image
make build

# Run the local dev environment
make devserver
```

The `build` script only needs to be run once, and it only needs to be re-run if the requirements.txt file gets changed.

`devserver` is a simple script that launches a postgres container in the background and connects an app container to it. It really is that simple.

As you edit files in the project, the dev server will live reload.

If you need to run any `manage.py` commands, you may do it like so:

```
docker exec -it gardenhub python manage.py <command>
```

## License

GardenHub is copyright © 2017 HarvestHub and licensed under the GNU AGPL version 3 or later. View the `LICENSE` file for a copy of the full license.
