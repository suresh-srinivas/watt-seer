import pytest
from app import server, app
from flask import session
import data_fetcher
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    server.config['TESTING'] = True
    server.config['WTF_CSRF_ENABLED'] = False
    with server.test_client() as client:
        with server.app_context():
            yield client

def test_root_route_redirects_to_login(client):
    """Test that the root route redirects to login when not authenticated"""
    response = client.get('/')
    assert response.status_code == 302
    assert response.location == '/login'

def test_login_page_loads(client):
    """Test that the login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Energy Data Dashboard' in response.data
    assert b'Username:' in response.data
    assert b'Password:' in response.data
    assert b'Utility:' in response.data

def test_login_with_valid_credentials(client):
    """Test login with valid credentials"""
    with patch('data_fetcher.get_current_month_data') as mock_get_data:
        mock_get_data.return_value = MagicMock()  # Return a mock DataFrame
        
        response = client.post('/login', data={
            'username': 'test@example.com',
            'password': 'testpass',
            'utility': 'portlandgeneral'
        })
        
        assert response.status_code == 302
        assert response.location == '/dashboard'
        
        # Check if session was created
        with client.session_transaction() as sess:
            assert 'user' in sess
            assert sess['user'] == 'test@example.com'
            assert 'utility' in sess
            assert sess['utility'] == 'portlandgeneral'

def test_login_with_invalid_credentials(client):
    """Test login with invalid credentials"""
    with patch('data_fetcher.get_current_month_data') as mock_get_data:
        mock_get_data.side_effect = Exception('Invalid credentials')
        
        response = client.post('/login', data={
            'username': 'wrong@example.com',
            'password': 'wrongpass',
            'utility': 'portlandgeneral'
        })
        
        assert response.status_code == 200
        assert b'Invalid credentials' in response.data
        
        # Check that session was not created
        with client.session_transaction() as sess:
            assert 'user' not in sess
            assert 'utility' not in sess

def test_dashboard_requires_login(client):
    """Test that dashboard is not accessible without login"""
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert response.location == '/login'

def test_dashboard_accessible_after_login(client):
    """Test that dashboard is accessible after successful login"""
    with patch('data_fetcher.get_current_month_data') as mock_get_data:
        mock_get_data.return_value = MagicMock()
        
        # First login
        client.post('/login', data={
            'username': 'test@example.com',
            'password': 'testpass',
            'utility': 'portlandgeneral'
        })
        
        # Then try to access dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200

def test_logout_clears_session(client):
    """Test that logout clears the session"""
    with patch('data_fetcher.get_current_month_data') as mock_get_data:
        mock_get_data.return_value = MagicMock()
        
        # Login first
        client.post('/login', data={
            'username': 'test@example.com',
            'password': 'testpass',
            'utility': 'portlandgeneral'
        })
        
        # Check session exists
        with client.session_transaction() as sess:
            assert 'user' in sess
            assert 'utility' in sess
        
        # Logout
        response = client.get('/logout')
        assert response.status_code == 302
        assert response.location == '/login'
        
        # Check session is cleared
        with client.session_transaction() as sess:
            assert 'user' not in sess
            assert 'utility' not in sess

def test_dash_routes_protected(client):
    """Test that Dash routes are protected"""
    response = client.get('/_dash/')
    assert response.status_code == 302
    assert response.location == '/login'

def test_assets_routes_protected(client):
    """Test that assets routes are protected"""
    response = client.get('/assets/')
    assert response.status_code == 302
    assert response.location == '/login' 