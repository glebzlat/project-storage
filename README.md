# Project Storage

## Development

The project is managed using [Poetry](https://python-poetry.org/).

Install the dependencies

```sh
poetry install --with=dev
```

Activate the environment

```sh
eval $(poetry env activate)
```

Run the `poe` commands:

```sh
poe test  # Unit testing
poe mypy  # Type checking
poe pep8  # PEP8 style checking
```

Create a `.env` file before launching the application, see `env.example`.

Start the development server:

```sh
fastapi dev src/project_storage/main.py
```

Test the API:

```sh
curl -X GET http://localhost:8000/api/healthcheck
```

Build and run the Docker container:

```sh
docker compose build
docker compose up
```

Perform database migration:

```sh
docker compose exec app alembic upgrade head
```

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
