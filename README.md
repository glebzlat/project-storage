# Project Storage

Project Storage is a service that manages projects and project resources. It
allows users to create projects, add project files, invite participants, and
transfer projects.

## Run

### 1. Configure environment

Use [`env.example`](./env.example) file to create a `.env`. Replace all
`<placeholders>` with your values.

### 2. Run the app

Build and run an application container.

```sh
docker compose --profile prod up --build
```

The service will be available on `http://localhost:8000`. View the API
documentation at `http://localhost:8000/docs`.

## Development

### 1. Install the dependencies

```sh
poetry install --with=dev
```

### 2. Development commands

Activate the environment:

```sh
eval $(poetry env activate)
```

Use the following command to run unit tests, MyPy type checker and Flake
style checker respectively:

```sh
poe unit_test
poe mypy
poe pep8
```

#### Unit tests

There is no additional requirements for running unit tests: they mock all
heavy-weight and external dependencies. Therefore it is always possible to
execute them locally just by typing

```sh
poe unit_test
```

#### Integration tests

Integration tests require a full infrastructure set up and running, so either
install and arm all the required services (look at `docker-compose.yml`)
or just use `docker compose`.

The command below builds and runs test service. Note that it rebuilds services
each time it is invoked. Also note that this command only runs integration
tests.

```sh
poe docker_test
```

### 3. Run an app

This step depends on [environment configuration step](#1-configure-environment)
described in the Run section.

Build and run the development service:

```sh
docker compose --profile dev up --build
```

Add `--watch` option in order to sync source file changes. FastAPI is launched
in the dev mode and will reload the changes.

### 4. Database migrations

Running application and database containers are required in order to perform
revisions and migrations. Run the `up` command in detached state or in watch
mode in a different terminal (I suggest using `tmux` for convenience).

```sh
docker compose exec app|app-dev alembic ...
```

Replace `app|app-dev` with one alternative matching the profile used to start
the containers.

## Used resources

### Anatomy of a Scalable Python Project (FastAPI)

- [YouTube video](https://youtu.be/Af6Zr0tNNdE?si=bnYKP1HSOUkPjj6K)
- [GitHub repo](https://github.com/ArjanCodes/examples/tree/main/2025/project)

### Poetry

- [Official doc](https://python-poetry.org/docs)
- [How to Build and Publish Python Packages With Poetry](https://www.freecodecamp.org/news/how-to-build-and-publish-python-packages-with-poetry/)

### Pytest

- [Pytest with Eric - Building And Testing FastAPI CRUD APIs With Pytest (Hands-On Tutorial)](https://pytest-with-eric.com/pytest-advanced/pytest-fastapi-testing)
- [CC410 - Test doubles in Pytest](https://textbooks.cs.ksu.edu/cc410/i-oop/10-test-doubles/08-pytest-test-doubles/index.html)

### Pydantic

- [Settings Management](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings)

### Docker & docker-compose

- [Docker Compose Tutorial](https://youtu.be/HG6yIjZapSA?si=9bUhemlm3I4AJsVc)
- [Build Production-Ready Docker Images with Python, Poetry & FastAPI](https://blogs.amplify.security/blog/how-to-build-production-ready-docker-images-with-python-poetry-and-fastapi)
- [Connecting FastAPI and PostgreSQL Across Separate Docker Compose Files](https://medium.com/@diwasb54/connecting-fastapi-and-postgresql-across-separate-docker-compose-files-a-developers-journey-5b116ed68212)
- [Discussion - Document docker poetry best practices](https://github.com/orgs/python-poetry/discussions/1879#discussioncomment-216865)
- [docker-compose-healthcheck](https://github.com/peter-evans/docker-compose-healthcheck)

### SQLAlchemy & Alembic

- [SQLAlchemy documentation](https://docs.sqlalchemy.org/)
- [Alembic documentation](https://alembic.sqlalchemy.org/)
- [Beginner’s Guide to Alembic and SQLAlchemy in Python](https://medium.com/@evembijo/beginners-guide-to-alembic-and-sqlalchemy-in-python-manage-your-database-like-a-pro-9395b5b5080d)
- [Solving the FastAPI, Alembic, Docker Problem](https://hackernoon.com/solving-the-fastapi-alembic-docker-problem)
