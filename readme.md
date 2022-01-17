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

## Production

### Linux (openrc, nginx, uWSGI)

#### Gentoo

Install `www-servers/uwsgi` with python support.

Link `uwsgi` service to `uwsgi.aucservice`. This service will be used to run uWSGI in "single-instance" mode rather than "emperror" mode.

```
# ln -s /etc/init.d/uwsgi /etc/init.d/uwsgi.aucservice
```

By default uWSGI service on Gentoo in single-instance mode reads configuration files in `/etc/conf.d/`. We need to make it read our configuration in INI format. Create `/etc/conf.d/uwsgi.aucservice` with the following line:

```
UWSGI_EXTRA_OPTIONS="--ini /etc/uwsgi.d/aucservice.ini"
```

Create INI configuration in `/etc/uwsgi.d/aucservice.ini`

```ini
# set correct python plugin version (may be python3 or python)
# set correct base path
# set SECRET_KEY environment variable

[uwsgi]
plugins = python39
app-name = aucservice

pidfile = /run/%(app-name).pid
socket = /run/%(app-name).sock
#http = :9090 # for testing
logto = /var/log/uwsgi/%(app-name).log
log-date = true

chown-socket = nginx:nginx
chmod-socket = 664

base = /srv/aucservice-api
chdir = %(base)
home = %(base)/venv
pytonpath = %(base)/venv

module=api
callable=app

processes=4
env=SECRET_KEY=change_me
```

You can use `http` mode instaed of `socket` to test the server. Comment out `logto` setting to log to stdout. You may need to add `,http` to `plugins`

```
# uwsgi --ini /etc/uwsgi.d/aucservice.ini
```

Add this to your nginx configuration

```
server {
		server_name aucservice.localdomain; # change to your domain name
		#listen 127.0.0.1; # for local debugging
		listen 80;

		access_log /var/log/nginx/aucservice.access_log main;
		error_log /var/log/nginx/aucservice.error_log info;

		location / {
			include uwsgi_params;
			uwsgi_pass unix:/run/aucservice.sock;
		}
}
```

#### Alpine

Install `uwsgi` and `uwsgi-python`.

The process of setting up uWSGI on Alpine is similar to Gentoo.

Copy `/etc/init.d/uwsgi` to `/etc/init.d/uwsgi.aucservice`, edit it and make it run as root instead of nobody in single-instance mode.

Create uWSGI INI config at `/etc/uwsgi/conf.d/aucservice.ini`.

Add nginx configuration.
