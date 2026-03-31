# Harness / Runtime / E2E Engineering

Testing is primarily done via pytest and mocked external IO boundaries to preserve deterministic tests.
E2E flows are verified by running `uv run main.py` against standard test files.
