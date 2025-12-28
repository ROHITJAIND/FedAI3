"""
Auth0 Setup Helper Script
Helps configure Auth0 authentication for the FedAI project
"""
import os
import secrets
from pathlib import Path


def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_hex(24)


def create_env_file():
    """Create .env file from template"""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled")
            return False
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return False
    
    print("\n🔐 Auth0 Configuration Setup")
    print("=" * 50)
    print("\nPlease enter your Auth0 application details:")
    print("(You can find these in your Auth0 dashboard)\n")
    
    # Get Auth0 credentials
    domain = input("Auth0 Domain (e.g., dev-abc123.us.auth0.com): ").strip()
    client_id = input("Auth0 Client ID: ").strip()
    client_secret = input("Auth0 Client Secret: ").strip()
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Create .env content
    env_content = f"""# Auth0 Configuration
# Created by setup script

# Your Auth0 Domain
AUTH0_DOMAIN={domain}

# Your Auth0 Client ID
AUTH0_CLIENT_ID={client_id}

# Your Auth0 Client Secret
AUTH0_CLIENT_SECRET={client_secret}

# Application Secret Key (auto-generated)
SECRET_KEY={secret_key}
"""
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print(f"📁 Location: {env_file.absolute()}")
    
    return True


def verify_auth0_settings():
    """Verify Auth0 settings in Auth0 dashboard"""
    print("\n📋 Auth0 Dashboard Configuration Checklist")
    print("=" * 50)
    print("\nPlease configure the following in your Auth0 application:\n")
    
    print("1️⃣  Allowed Callback URLs:")
    print("   http://localhost:5000/callback")
    print("   http://localhost:5001/callback")
    print("   http://localhost:5002/callback")
    
    print("\n2️⃣  Allowed Logout URLs:")
    print("   http://localhost:5000")
    print("   http://localhost:5001")
    print("   http://localhost:5002")
    
    print("\n3️⃣  Allowed Web Origins:")
    print("   http://localhost:5000")
    print("   http://localhost:5001")
    print("   http://localhost:5002")
    
    print("\n💡 These settings are required for authentication to work correctly.")
    print("   Copy and paste them into your Auth0 application settings.\n")


def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    
    try:
        import authlib
        print("✅ authlib installed")
    except ImportError:
        print("❌ authlib not installed")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    return True


def main():
    """Main setup function"""
    print("\n" + "=" * 50)
    print(" " * 10 + "Auth0 Setup Helper")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies!")
        print("📝 Install them with: pip install -r requirements.txt")
        return
    
    # Check if already configured
    env_file = Path('.env')
    if env_file.exists():
        print("\n✅ .env file already exists")
        print("📝 To reconfigure, delete .env and run this script again")
        verify_auth0_settings()
        return
    
    # Create .env file
    if create_env_file():
        verify_auth0_settings()
        
        print("\n🎉 Setup Complete!")
        print("\n📚 Next Steps:")
        print("   1. Configure the URLs above in your Auth0 dashboard")
        print("   2. Run your hospital interface:")
        print("      python hospital_interface.py --hospital A --port 5000")
        print("\n📖 For more details, see AUTH0_SETUP.md\n")
    else:
        print("\n❌ Setup failed!")


if __name__ == '__main__':
    main()
