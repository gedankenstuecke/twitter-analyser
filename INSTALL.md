# Install
[TwArχiv](http://twarxiv.org) is a Django application that interfaces with [Open Humans](https://openhumans.org)
for the file storage and user management and that is designed to be deployed to *Heroku*. As such there are some dependencies and intricacies that need to be taken into account.
NOTE: We recommend installation on python3.

## Dependencies

### Database(s)
TwArχiv uses two kinds of databases for short- and long-term storage. The short term storage (for managing tasks that are not run on the webserver) is done with `redis` while the long-term storage is done with `postgresql`. If you are deploying to the heroku production environment you just have to click the appropriate add-ons.

For your development environment you have to install both `redis` and `postgresql` on your local machine.
If you are running MacOS and using `brew` (or are a user of `linuxbrew`) you can easily install both with the following commands:

```
brew install redis
brew install postgresql
```

You can then easily run `redis-server` from your command line to start an instance of `redis`.
The configuration of `postgres` can be a bit more involved. [Check out this blogpost for some tips](https://www.codementor.io/devops/tutorial/getting-started-postgresql-server-mac-osx).

### Python modules
Django in general and TwArχiv in particular requires a larger set of `python` libraries. The current list can be found in the `requirements.txt` in this repository. Right now the requirements are the following:

```
gunicorn==19.7.1
pytz==2017.2
gender_guesser==0.4.0
pandas==0.20.3
tzwhere==3.0.3
Django==1.11.3
dj-database-url==0.4.2
whitenoise==3.3.1
psycopg2==2.7.3.1
redis==2.10.6
celery==4.1.0
requests==2.18.4
timezonefinder==2.1.2
geojson==2.3.0
arrow==0.12.0
```

If you are using `heroku` in your development environment it should take care of installing the modules listed in `requirements.txt` automatically.

## Create a Project on Open Humans
We want to interface with Open Humans for our project. For this reason we need to create a research project on openhumans.org. After creating an account go to https://www.openhumans.org/direct-sharing/projects/manage/
and generate a new _OAuth_ project. The most important parts to get right are the `enrollment URL` and the `redirect URL`. For your development environment this should be the right URLs:

```
enrollment: http://127.0.0.1:5000/users/
redirect: http://127.0.0.1:5000/users/complete # no trailing slash!
```

## Start development environment
All good so far? Then we can now start developing in our local environment.
I recommend using the `heroku-cli` interface to boot up both the `celery`-worker as well as the `gunicorn` webserver. You can install the CLI using `brew install heroku/brew/heroku` (or however that works on non-macs). If you are in the root directory of this repository and run `heroku local:run python manage.py migrate`, it will perform migrations to the database. `heroku local` will then use the `Procfile` to spawn local web & celery servers. If you've configured everything correctly you should be able to point your browser to `http://127.0.0.1:5000/` and see your very own copy of TwArχiv

#### Heroku configuration
`heroku` will try to read environment variables from `.env` for your local environment. Make sure you have such a file. It should contain the following keys:

```
REDIS_URL=redis:// # where is your redis server located? most likely at this url if in dev
DATABASE_URL=postgres:///username # where does your postgres DB live?
SECRET_KEY=foobar # the Django Secret Key
ON_HEROKU=False # is our app deployed on heroku?
OH_CLIENT_ID=NOT_A_KEY_EITHER # the client ID for your Open Humans project
OH_CLIENT_SECRET=NOTAREALKEY # the secret key you get from Open Humans when creating a project.
OH_ACTIVITY_PAGE=https://www.openhumans.org/activity/your-activity-name/ # What is your Project on Open Humans?
APP_BASE_URL=http://127.0.0.1:5000/users # where is our app located? Open Humans wants to know

PYTHONUNBUFFERED=true # make sure we can print to console
```

This file contains private data that would allow other parties to take over your project. So make sure that you **don't commit this file to your Git repository**.

## Deploy to `heroku` production
Once it's set up it is as easy as running `git push heroku master`. For obvious reasons (see above) it won't have the `.env` file for setting the environment variables. For that reason you have to manually specify them for the production environment. The `heroku cli` makes this easy:

```
heroku config:set SECRET_KEY=foobar
heroku config:set APP_BASE_URL=http://www.example.com
```

**You don't have to set the `REDIS_URL` and `DATABASE_URL` in production. This will be done by heroku!**
