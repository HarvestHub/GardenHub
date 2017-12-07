![GardenHub Promo Banner](gardenhub-promo.png)

[![Build Status](https://travis-ci.org/HarvestHub/GardenHub.svg?branch=master)](https://travis-ci.org/HarvestHub/GardenHub)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# GardenHub

Formed around the simple idea that food should not go to waste, GardenHub is the solution to the problem of community garden food waste. Despite the best efforts of community gardeners, far too often food produced in community gardens rots on the vine.

GardenHub is building technology to enable gardeners to collaborate and act upon what's growing, ripening, and available for harvest in their gardens. Using this information, GardenHub notifies gardeners, local charities, restaurants, and other stakeholders of the availability of this food.

<img src="gardenhub-screenshot.png" alt="GardenHub Mobile Screenshot" height="640">

## WIP

GardenHub is a work in progress web application being developed in the open. It's licensed under AGPL-3.0+ and written in Python using the Django framework. You can preview our work on the [demo site](http://gardenhub.candlewaster.co/), but keep in mind that it will change dramatically.

Eventually, the inner-workings of this project will be documented in detail. We're making an effort to self-document the code, so take a look. You're welcome to chat with us by opening a GitHub issue. GardenHub is a project by HarvestHub, and it's being developed by Candlewaster.

## Local development

You will need [virtualenvwrapper](http://virtualenvwrapper.readthedocs.io/en/latest/), git, lessc, and Python 3 installed.

```
# Clone the repo
git clone https://github.com/HarvestHub/GardenHub.git

# Enter the project folder
cd GardenHub

# Create the Python virtual environment
mkvirtualenv gardenhub --python=python3

# Install project dependencies
pip install -r requirements.txt

# Create the sqlite3 database
python manage.py migrate

# Run the local development server
python manage.py runserver
```

### Pull the staging database
If you have permission to access the staging server, you may pull the staging database locally by running `make pull_dev_db` in the project directory.

## License

GardenHub is copyright © 2017 HarvestHub and licensed under the GNU AGPL version 3 or later. View the `LICENSE` file for a copy of the full license.
