import sys
import pytest

sys.path.insert(0, '/app/workspace/src')
try:
    from api import app
except ImportError:
    app = None

@pytest.fixture
def client():
    if app:
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    else:
        yield None
