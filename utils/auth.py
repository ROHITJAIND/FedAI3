"""
Auth0 Authentication Helpers
Provides decorators and utilities for protecting routes
"""
from functools import wraps
from flask import session, redirect, url_for, request
import urllib.parse


def login_required(f):
    """
    Decorator to require authentication for a route
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "This is protected"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # Store the URL they were trying to access
            session['next_url'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the current logged-in user from session"""
    return session.get('user')


def is_authenticated():
    """Check if the current user is authenticated"""
    return 'user' in session


def get_user_info():
    """Get detailed user information from session"""
    user = session.get('user')
    if not user:
        return None
    
    return {
        'name': user.get('name', 'Unknown'),
        'email': user.get('email', 'No email'),
        'picture': user.get('picture', ''),
        'sub': user.get('sub', ''),
        'nickname': user.get('nickname', user.get('name', 'User'))
    }


def get_logout_url(domain, client_id, return_to):
    """
    Generate Auth0 logout URL
    
    Args:
        domain: Auth0 domain
        client_id: Auth0 client ID
        return_to: URL to redirect to after logout
    
    Returns:
        str: Complete logout URL
    """
    params = {
        'client_id': client_id,
        'returnTo': return_to
    }
    
    return f'https://{domain}/v2/logout?{urllib.parse.urlencode(params)}'
