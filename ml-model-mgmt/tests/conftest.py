import sys
import pytest

sys.path.insert(0, '/app/workspace/src')
try:
    from api import app
except Exception as error:
    print(f"[conftest] Failed to import app: {error}", file=sys.stderr, flush=True)
    app = None

@pytest.fixture
def client():
    if app:
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    else:
        yield None
