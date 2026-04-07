# Backend Tests

This directory contains test scripts for validating backend functionality.

## Files

- `final_test.py` - Final comprehensive test suite
- `test_complete_import.py` - Tests complete import functionality
- `test_import.py` - Tests import operations
- `test_import_endpoint.py` - Tests API import endpoints
- `test_views_import.py` - Tests view-related import functionality

## Usage

Run these tests to validate backend functionality:

```bash
python tests/test_import.py
python tests/final_test.py
```

Or run all tests:
```bash
python -m pytest tests/  # if using pytest
```