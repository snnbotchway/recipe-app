# Recipe-App-API

The API for a recipe management application.

## Installation

After you cloned the repository, you want to install and set up docker desktop for your operating system.

## Usage

For development, run all the services with docker compose:

`docker compose up`

This will start the API app and database services for development.

For production(On a virtual server):

1. Set up environment variables by renaming the `.env.sample` file to `.env`.

2. Edit the variables accordingly but provide a secure secret key and database password. You can generate a secure secret key [here](https://djecrety.ir/).

    The DJANGO_ALLOWED_HOSTS variable has to be a comma(,) separated list of allowed hosts.

3. Run all the services with `docker compose -f docker-compose-deploy.yml up`

    This will start the API app and database, along with a reverse proxy.

## Documentation

Automatic documentation is provided with Swagger/OpenAPI and can be found on the homepage.
