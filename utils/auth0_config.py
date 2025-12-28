"""
Auth0 Configuration
Loads Auth0 settings from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Auth0Config:
    """Auth0 configuration settings"""
    
    # Auth0 Application Settings
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
    AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    
    # Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # Auth0 URLs
    @property
    def AUTH0_AUTHORIZE_URL(self):
        return f'https://{self.AUTH0_DOMAIN}/authorize'
    
    @property
    def AUTH0_TOKEN_URL(self):
        return f'https://{self.AUTH0_DOMAIN}/oauth/token'
    
    @property
    def AUTH0_USERINFO_URL(self):
        return f'https://{self.AUTH0_DOMAIN}/userinfo'
    
    @property
    def AUTH0_LOGOUT_URL(self):
        return f'https://{self.AUTH0_DOMAIN}/v2/logout'
    
    # OAuth2 Configuration
    OAUTH2_CONFIG = {
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'server_metadata_url': f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration',
        'client_kwargs': {
            'scope': 'openid profile email',
        }
    }
    
    def validate(self):
        """Validate that all required Auth0 settings are configured"""
        missing = []
        
        if not self.AUTH0_DOMAIN:
            missing.append('AUTH0_DOMAIN')
        if not self.AUTH0_CLIENT_ID:
            missing.append('AUTH0_CLIENT_ID')
        if not self.AUTH0_CLIENT_SECRET:
            missing.append('AUTH0_CLIENT_SECRET')
        
        if missing:
            raise ValueError(
                f"Missing required Auth0 configuration: {', '.join(missing)}. "
                f"Please set these in your .env file."
            )
        
        return True


# Global config instance
auth0_config = Auth0Config()
