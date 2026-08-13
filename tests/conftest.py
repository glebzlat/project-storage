import pytest


def pytest_collection_modifyitems(config, items):
    for i in items:
        if "tests/api" in str(i.fspath):
            i.add_marker(pytest.mark.integration)
        if "tests/unit" in str(i.fspath):
            i.add_marker(pytest.mark.unit)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line("markers", "unit: marks tests as unit tests")

