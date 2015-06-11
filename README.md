# Docker Workshop
In this workshop you will learn the basics of `docker`, `docker-compose`, and `Swagger` through
creating a small collection of microservices and writing documentation/tests for them. No Django or
Python experience is assumed, but it is helpful. Code for the web applications is written in Python,
but for the purposes of this workshop mostly involves editing configuration-like files.

## Summary of Workshop
You will build/complete a django web application (written in Python). The core logic has been
written for you, the majority of the areas to fill in are related to configuration. The goal isn't
to learn `django`, it is to learn `docker`.

### Backend JSON API
The backend API is nothing more than a thin wrapper around the Google Places API.

In this portion you will learn:
* How to write a `Dockerfile`
* How to use docker cli
* How to use docker-compose cli

Completing this app will require passing environment variables/configuration files around
correctly so that the secret API key is not in version control, but can be accessed by the app.
The app itself will be one Docker container.

The application also incorporates liberal use of caching. The application in production mode is
configured to cache: requests to the application and external API calls. This is accomplished
by using a `redis` container linked to the web server container.

### Frontend JSON API
The frontend API has three endpoints:
* `/view`: forwards request to backend to get a list of places based on `keywords` and `location`
* `/save`: does the same as `/view` but saves the returned locations in postgres database
* `/show`: lists all saved locations with timestamps

### Nginx reverse proxy
As with most web applications, things should be behind a reverse proxy of some variety. In this
workshop you will learn how Nginx can be configured to accomplish this.

### Swagger Docs and Testing
Its standard practice after implementing an API to test and/or document it. Unfortunately,
documentation has a tendency to fall out of sync with the code..

Swagger provides two powerful capabilities that help prevent this from happening:

1. Expressive and descriptive language for specifying the schema for JSON APIs
2. Based on that schema it can generate client API libraries in a variety of languages.

To insure that documentation, tests, and code are in sync, you can write Swagger docs, generate
API clients, then use that exclusively for writing integration tests. This enforces that the three
are always in sync.

# Installation and Setup
In this section the goal is to:

* Install Docker, docker-compose, and boot2docker.

## Terminology
Lets get some terminology out of the way
* Docker daemon: background service which manages running containers
* Docker host: the machine running the Docker daemon
* Docker client: the machine/process executing docker commands (eg build, run)

## Install boot2docker
Docker does not run natively on OSX. To work around that, boot2docker seamlessly sets up a
VirtualBox machine running a distribution of Linux which runs Docker. It also correctly maps
settings so that it can be accessed seamlessly from your OSX machine.

[Install boot2docker](http://boot2docker.io/)

Useful tips:
* By default, the docker host is reachable by the ip address of the VirtualBox VM. This can get
annoying. You can improve this by using `echo $DOCKER_HOST`, extracting the ip address, then
putting an entry in `/etc/hosts` that looks like `192.168.59.103 drydock`. This will map the host
`drydock` to the VirtualBox VM, making testing things such as web applications in the browser
nicer
* Useful commands: boot2docker up, boot2docker down, boot2docker ip. These can run/stop the VM
and print its ip address

## Install Docker
Now that there is a Docker host/daemon running, you need to install the client application so you
can manage/use it. Installation instructions can be found at
[docker.io](https://docs.docker.com/installation/).

## Install docker-compose
The final thing you need to install is docker-compose. This is a tool which uses configuration file
to coordinate running ordinary Docker commands. Everything docker-compose does, can be done with
regular Docker commands, but it makes it much easier.

[Install docker-compose](https://docs.docker.com/compose/install/)

NOTE: if you run into permissions issues, download the binary using curl to your downloads
directory, then rename it to docker-compose, chmod it, then move it to `/usr/local/bin`.

## Install Python
Although we will be working mostly within Docker containers, it would be helpful to have a recent
Python installation. For Macs, you can run `brew install python`. Also make sure that Python's
package manager (pip) is installed. When this is done, execute `pip install -r requirements.txt`
within this directory. If you would like to avoid dependency conflicts with existing projects, you
can make use of [virtualenv](https://virtualenv.pypa.io/en/latest/)

## API Key Setup
Before getting started, you will need to signup for the
[google API console](https://console.developers.google.com/project). Once you complete adding a
project, enable the Google Places API for Webservices (APIs & auth -> APIs). Next you will need to
generate credentials for reaching the API (APIs & auth -> credentials). Use the "Public API Access"
option to create a "server key". The last step will be to save this API key in a suitable location.

One way to do this is to create a bash script at `~/.secrets`. The file should look like:
```bash
export GOOGLE_PLACE_API_KEY=mysecretgoeshere
```

Then add this line to your `~/.bashrc`: `source ~/.secrets`.

Lets test that you can reach the Google Place API. As part of the python installation
(with `requirements.txt`) you also implicitly installed the python library we will use with the
Google Places API. To test, start a python terminal session by typing `python` into your terminal.
Then execute each line below:

```python
import os
from googleplaces import GooglePlaces

API_KEY = os.getenv("GOOGLE_PLACE_API_KEY")
google_places = GooglePlaces(API_KEY)

query_result = google_places.nearby_search(radius=50000, location='San Francisco, CA', keyword='climb touchstone')

for place in query_result.places:
    print place.name
```

The result should be a list of all the Touchstone climbing gyms in the area:
* Mission Cliffs
* Diablo Rock Gym
* Berkeley Ironworks
* The Studio Climbing
* Great Western Power Company

Also take note that this allowed you to access the API secret key without committing it to the
source. We will use a similar technique later on with Docker. In anticipation of this, browse
to `/docker-workshop/backend/environment`, copy `secrets.txt.template` to `secrets.txt`, then
input your API key. While you are at it, set the django secret key as well.

## Backend API
This first part of the project is mostly written for you to use as a reference
when working on the frontend API. Below is a summary of each file and its role within `backend`:

### Files:
* Dockerfile: define application build
* compose-common.yml: sourced by compose-development.yml and compose-production.yml
* docker-entrypoint.sh: executable file run by the container built by `Dockerfile`
* manage.py: entrypoint for various django administration commands
* requirements.txt: list of python requirements for project
* environment/secrets.txt: copied from secrets.txt.template and not in version control
* backend: contains django project. Particular attention should be paid to `backend/settings`
since you may need to configure variables here soon.
* places: django app with code for fetching google places data. You shouldn't need to change
anything in here

### Dockerfile
The `Dockerfile` is responsible for configuring our application and turning it into an image. You
will write the `Dockerfile` knowing that:
* You should use the official python 2 image as a base
* Set the environment variable "PYTHONUNBUFFERED" to 1
* The contents of `backend` (at root of repo) should end up in `/web` in the container.
* The current working directory should end up being `/web`
* The python requirements in `requirements.txt` need to be installed via
`pip install -r requirements.txt`
* Port 8000 should be exposed
* Add a volume at `/web`, this will be explained later
* Set the entrypoint of the container to be `docker-entrypoint.sh`

You may find the reference at [docker.com](https://docs.docker.com/reference/builder/) useful.
Below is a list of the directives required to do the above with short descriptions.
* FROM: specifies which image should be used as a base
* ENV: sets environment variables
* ADD: copy file from the host to the container
* WORKDIR: change the current directory
* RUN: execute the given command
* EXPOSE: expose port on container to outside world
* VOLUME: add a volume which the host can mount onto
* ENTRYPOINT: set the container's entrypoint command

Next up, lets try to build and run the application container. It is highly recommended to use the
`--help` flag on the docker cli. It is a simple and concise way
to learn what commands and options are available. Try doing `docker --help` now to see what
commands there are.

There are quite a few, below are the most commonly used and most helpful:
* build: builds a new image based on a Dockerfile.
* exec: run a command within an already running container. This is extremely helpful for debugging.
In practice you would use `docker exec -it image_name bash`. This tells docker to execute bash,
interactively (-i) with pseudo-TTY allowing you to run arbitrary bash commands interactively.
* run: run an already built image as a new container
* kill: stop a running container
* rm: remove a stopped container
* logs: prints a containers logs. This is useful for debugging problems when running containers in
the background

Now, lets try building and running the application. Keep in mind we need to:
* Pass the API secret key to `docker run`
* Set `DJANGO_MODE` to development
* Bind the host port 8000 to the container exposed port 8000

You may find the following flags helpful for building:
* -t: tag the image with a name

You may find the following flags helpful for running:
* -e: set environment variables, such as your API key (we will learn soon how to set it in a better
way)
* --name: name the container. By default Docker assigns a random name
* -p: configure exposed ports

After running the correct command, browse to
[http://drydock:8000/places?location=san%20francisco&keywords=climbing](http://drydock:8000/places?location=san%20francisco&keywords=climbing)
to check if the web app is running. You may need to replace `drydock` with your VMs IP address.

### docker-compose
For the backend, the compose files have already been written for you. This should provide a good
example of a `docker-compose` configuration file and allow you to learn the `docker-compose` cli.
In the portion covering the frontend, you will write your own `docker-compose` configuration file.

In general, `docker-compose` is "simply" a wrapper around the `docker` cli. Anything you can do in
`docker-compose` you can do with sufficient effort in `docker`.

The default name for a `docker-compose` configuration file is `docker-compose.yml`. If the file is
named something different, you will have to inform the cli of this difference. The configuration is
also in yaml format. Open `compose-common.yml`, `compose-development.yml`, and
`compose-production.yml` which configure `django` to work with `redis` in production and development
configurations.

It will also be helpful to open the [docker-compose reference](https://docs.docker.com/compose/yml/)



#### Configuration
`docker-compose` supports limited, but useful inheritance functionality. In this file we define
the basic things about the `web` container and `redis` container that will be common across both
development and production configurations.

* build: specifies to build `web` with `Dockerfile` in the current directory
* image: specifies to pull the official `redis` image
* ports: bind the host port 8000 to the container port 8000
* links: allow the given container connect to the other one seamlessly using the link name as the host
* environment: supply environment variables
* env_file: supply environment variables from a file
* volumes: mount the current directory as a volume in the container. This is helpful for live coding
without having to rebuild the container (django picks up changes and relaunches as well)

#### Running
Now it is time to launch our application. Before we launched our app with `docker`, but that didn't
launch it with `redis` as well. Lets launch it once in each of development and production modes by
using `compose-development.yml` and `compose-production.yml` respectively.

As before `docker-compose --help` is very useful. The below commands are useful:
* build: build any requisite images
* up: start the set of containers
* kill: kill containers running in background
* rm: remove containers, useful to try if you are seeing odd behavior
* -d: run in daemon mode
* -f: tell `docker-compose` which configuration file to use

Using the above and documentation, launch the set of services in development and then in production,
killing/removing the containers in between. For each one
1. Browse to [http://drydock:8000/places?keywords=climbing&location=oakland](http://drydock:8000/places?keywords=climbing&location=oakland)
2. Notice the print message on the first request, then on a subsequent repeated request.
3. Now try requesting the same url, except add another random query string parameter such as `hi=1`.
This should cause the request cache to fail in production, but it should not issue an api request.

#### How Redis was configured
To see how redis was configured in the django application, browse to `backend/settings/production.py`.
Within here, find the `CACHES` statement. In particular `"LOCATION": "redis://redis:6379/1"` configures
django to communicate with the host named `redis`, which is the hostname given to the `redis` container
since the link name was `redis` (much redis, much redis...).

### Summary
In this section you should have:
1. Learned how to create a `Dockerfile`
2. Learned how to use the `docker` cli
3. Leanred how to use the `docker-compose` cli
4. Seen an example of `docker-compose` configuration files that can be used in development and
production.

## Frontend API
Before diving into what you will do now, here is a summary of the API:
1. `/api/view`: Provide `location` and `keywords` param and request is forwarded to backend api
2. `/api/save`: Same as view, but will save the locations fetched. Normally mutating behavior with
a GET is a nono, but it made my life easier...
3. `/api/show`: Show a list of all saved locations and dates they were saved

In this section the frontend api to call the backend api has been written for you. The application
has the appropriate python configuration files and a `Dockerfile` but is missing `docker-compose`
configuration. For the moment, we won't worry about separate configuration files for production
and development, and will hardcode environment variables setting the application mode. To get the
app running, you will need to:
* Create a web container building the `frontend` directory `Dockerfile`
* Expose port 8001 on the host binding to the container port 8000. Binding to the host port 8000
would cause a collision with the backend configured port.
* Create a postgres container. Note the postgres password and username need to be configured via
environment variables using `POSTGRES_PASSWORD` and `POSTGRES_USER` as described below.
* Create a link from the web container to the database container

It will be helpful to know
* The hostname of the database container should be `db`
* The username of the database should be `trulia`
* The password of the database should be taken from `secrets.txt` and passed using
`POSTGRES_PASSWORD`

Unfortunately, the application still won't work because there is nothing telling it about how
to reach the backend api. Within `frontend/api/views.py` you will notice a variable `BACKEND_API_URL`.
This configures where the application should look for the API using knowledge about linked services.
of the container (eg `backend_web_1`).

Now the service should be fully running. Browse to [http://drydock:8001/api/show](http://drydock:8001/api/show)
or one of the other urls to test the application.

It turns out, there is a better and more general way (albeit more complex) to allow APIs to
communicate with each other.

## Nginx
There are two issues with the prior approach:
1. The requests are not being load balanced
2. The above method does not extend to services which are interpendent. To make links, the container
being linked to must already be running and by definition will not be linked to anything. This would
not play well with for example a user service and a blog service. Links only work for services with
a dependency graph that forms a directed acyclic graph (DAG).

The easiest work around to this problem is to allow the containers making API calls to know what
is the ip address of the host machine, then bind a Nginx instance to reverse proxy/load balance
requests.

You can do this using a piece of code from the Docker documentation:
```bash
HOST_IP=`ip route show 0.0.0.0/0 | grep -Eo 'via \S+' | awk '{ print \$2 }'` gunicorn -b 0.0.0.0:8000 frontend.wsgi
```

The code above will do a lookup of the host ip, then pass it along as `HOST_IP` to the container.
This is the first piece of what we need to get Nginx running and is already included in the
`docker-entrypoint.sh` in the frontend service. You will also need to go into `frontend/api/views.py`
and switch the commented lines for `BACKEND_API_URL`. You should be able to retest this and see that
it works since it is still reaching the same VirtualBox VM that docker is running at on the same
port. Now remove the `external_link` from your compose configuraiton. The next step is to configure Nginx.

### Nginx configuration
Within the `nginx` folder there are all the required files in order to launch the reverse proxy
fully configured. Unfortunately `nginx` does not allow access to environment variables in its
configuration so the strategy used is to:
1. Create a template nginx configuration file, with `DOCKER_IP` as a placeholder for the true
ip address
2. Run a python script which has the `HOST_IP` passed in like before, and interpolates the value
into the nginx template file to create the actual configuration file.
3. Run nginx with the generated configuration file.

Now go back to `frontend/api/views.py` and change the port for `BACKEND_API_URL` to port `80`. This
will point the requests to hit the `nginx` server, which will forwarded/load balance them to
the backend server.

Lastly, run the nginx container with:
```bash
cd docker-workshop/nginx
docker build -t workshop-nginx .
docker run --name workshop-nginx -p 80:80 workshop-nginx
```

Now you should have the full application running: backend, frontend, and nginx tying them together.

# Swagger
WIP/TBD soon.

# Licensing
This workshop, including code and documentation is licensed under the Creative Commons Attribution
ShareAlike 4.0 International License and the MIT license. Details for each license are below and
in LICENSE.

## MIT License
The MIT License (MIT)

Copyright (c) 2015 Pedro Rodriguez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Creating Commons License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
