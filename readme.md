# Auction Service Api

REST API for the auction service application.

# Installation

## Development

Poetry is used to manage dependencies.

```bash
# install poetry if not already installed
$ pip install --user poetry

# switch into poetry shell
$ poetry shell

# install dependencies
$ poetry update

# set FLASK_APP to main application file
$ export FLASK_APP=api.py

# enable debug mode
$ export FLASK_DEBUG=1

# start development server
$ flask run
```
