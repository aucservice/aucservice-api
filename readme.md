# Auction Service Api

REST API for the auction service application.

# Installation

## Development

### Linux

```bash
# create virtualenv at venv
$ virtualenv venv

# activate virtualenv
$ source ./venv/bin/activate

# install dependencies
$ pip install -r requirements.txt 

# set FLASK_APP to main application file
$ export FLASK_APP=api.py

# enable debug mode
$ export FLASK_DEBUG=1

# set the secret key
$ export SECRET_KEY=some_string

# start development server
$ flask run
```

### Windows (powershell)

```powershell
# install virtualenv if not installed
PS> pip install --user virtualenv

# create virtualenv at venv
PS> python -m virtualenv venv

# activate virtualenv
PS> .\venv\Scripts\activate 

# install dependencies
PS> pip install -r requirements.txt 

# set FLASK_APP to main application file
PS> $env:FLASK_APP='api.py'

# enable debug mode
PS> $env:FLASK_DEBUG=1

# set the secret key
PS> $env:SECRET_KEY='some_string'

# start development server
PS> flask run
```
