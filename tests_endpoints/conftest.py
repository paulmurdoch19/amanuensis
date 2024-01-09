import pytest
from mock import patch, MagicMock
from amanuensis import app, app_init
from amanuensis.models import AssociatedUserRoles
import requests


app_init(app, config_file_name="amanuensis-config.yaml")

@pytest.fixture(scope="session")
def app_instance():
    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def client(app_instance):
    with app_instance.test_client() as client:
        yield client

@pytest.fixture(scope="session")
def session(app_instance):
    with app_instance.app_context():
        yield app_instance.scoped_session


@pytest.fixture(scope="session", autouse=True)
def patch_auth_request(app_instance):
    # Mock the auth_request method to always return True
    with patch.object(app_instance.arborist, 'auth_request', return_value=True):
        yield

@pytest.fixture(scope="session", autouse=True)
def patch_get_jwt_from_header():
    # Mock the get_jwt_from_header function to always return "1.2.3"
    with patch('amanuensis.auth.auth.get_jwt_from_header', return_value='1.2.3'):
        yield


# Add a finalizer to ensure proper teardown
@pytest.fixture(scope="session", autouse=True)
def teardown(request, app_instance, session):
    def cleanup():
        session.remove()
        # Explicitly pop the app context to avoid the IndexError
        #app_instance.app_context().pop()

    request.addfinalizer(cleanup)

