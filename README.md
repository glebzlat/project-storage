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
