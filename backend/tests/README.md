# Backend Tests

This directory contains all backend tests organized by type and functionality.

## Structure

```
tests/
├── __init__.py                 # Tests package
├── conftest.py                 # Shared pytest fixtures and configuration
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_user_dao.py       # UserDAO unit tests
│   └── test_user_service.py   # UserService unit tests
└── integration/                # Integration tests
    ├── __init__.py
    └── test_cognito_setup.py   # Cognito service integration tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, methods, or classes
- **Dependencies**: Mocked or minimal
- **Speed**: Fast execution

**Current Tests:**
- `test_user_dao.py`: Tests for UserDAO class ensuring proper Pydantic object returns
- `test_user_service.py`: Tests for UserService class and dependency injection

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and external services
- **Scope**: Multiple components working together
- **Dependencies**: Real or simulated external services
- **Speed**: Slower execution

**Current Tests:**
- `test_cognito_setup.py`: Tests Cognito service configuration and integration

## Running Tests

### All Tests
```bash
python -m pytest
```

### Unit Tests Only
```bash
python -m pytest tests/unit/
```

### Integration Tests Only
```bash
python -m pytest tests/integration/
```

### Specific Test File
```bash
python -m pytest tests/unit/test_user_dao.py
```

### With Coverage
```bash
python -m pytest --cov=app tests/
```

### Verbose Output
```bash
python -m pytest -v
```

## Test Fixtures

### Shared Fixtures (conftest.py)
- `db`: Test database session with automatic cleanup
- `user_dao`: UserDAO instance for testing
- `user_service`: UserService instance with injected dependencies

## Test Database

Tests use SQLite in-memory databases for isolation and speed. Each test gets a fresh database instance through the `db` fixture.

## Dependencies

Required packages for testing:
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pydantic[email]`: Email validation support

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use fixtures for setup/teardown
3. **Naming**: Use descriptive test names
4. **Assertions**: Test one thing per test
5. **Mocking**: Mock external dependencies in unit tests
6. **Documentation**: Add docstrings to test functions

## Adding New Tests

1. **Unit Tests**: Add to `tests/unit/` directory
2. **Integration Tests**: Add to `tests/integration/` directory
3. **Fixtures**: Add shared fixtures to `conftest.py`
4. **Naming**: Follow `test_*.py` naming convention
5. **Imports**: Use relative imports from `app` package
