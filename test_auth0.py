"""
Test Auth0 Configuration
Verifies that Auth0 is properly configured
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


def test_auth0_config():
    """Test Auth0 configuration loading"""
    print("\n" + "=" * 50)
    print("Testing Auth0 Configuration")
    print("=" * 50 + "\n")
    
    try:
        from utils.auth0_config import auth0_config
        print("✅ Auth0 config module imported successfully")
        
        # Check if .env exists
        env_file = Path('.env')
        if not env_file.exists():
            print("⚠️  .env file not found")
            print("📝 Run: python setup_auth0.py")
            return False
        
        print("✅ .env file exists")
        
        # Validate configuration
        try:
            auth0_config.validate()
            print("✅ Auth0 configuration is valid")
            
            # Display (masked) configuration
            print("\n📋 Configuration:")
            print(f"   Domain: {auth0_config.AUTH0_DOMAIN}")
            print(f"   Client ID: {auth0_config.AUTH0_CLIENT_ID[:8]}...")
            print(f"   Client Secret: {'*' * 20}")
            print(f"   Secret Key: {'*' * 20}")
            
            # Test URLs
            print("\n🔗 Auth0 URLs:")
            print(f"   Authorize: {auth0_config.AUTH0_AUTHORIZE_URL}")
            print(f"   Token: {auth0_config.AUTH0_TOKEN_URL}")
            print(f"   Userinfo: {auth0_config.AUTH0_USERINFO_URL}")
            print(f"   Logout: {auth0_config.AUTH0_LOGOUT_URL}")
            
            print("\n✅ All tests passed!")
            print("\n📝 Next steps:")
            print("   1. Configure callback URLs in Auth0 dashboard")
            print("   2. Run: python hospital_interface.py --hospital A --port 5000")
            
            return True
            
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("📝 Fix your .env file or run: python setup_auth0.py")
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📝 Install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_auth_helpers():
    """Test authentication helper functions"""
    print("\n" + "=" * 50)
    print("Testing Auth Helper Functions")
    print("=" * 50 + "\n")
    
    try:
        from utils.auth import login_required, get_current_user, is_authenticated, get_user_info
        print("✅ Auth helpers imported successfully")
        
        # Test that decorators exist
        print("✅ @login_required decorator available")
        print("✅ get_current_user() function available")
        print("✅ is_authenticated() function available")
        print("✅ get_user_info() function available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_dependencies():
    """Test required packages"""
    print("\n" + "=" * 50)
    print("Testing Dependencies")
    print("=" * 50 + "\n")
    
    packages = {
        'authlib': 'Auth0 OAuth library',
        'dotenv': 'Environment variable loader',
        'flask': 'Web framework',
        'requests': 'HTTP library'
    }
    
    all_ok = True
    for package, description in packages.items():
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package:15} - {description}")
        except ImportError:
            print(f"❌ {package:15} - {description} (NOT INSTALLED)")
            all_ok = False
    
    if not all_ok:
        print("\n📝 Install missing packages: pip install -r requirements.txt")
    
    return all_ok


def main():
    """Run all tests"""
    print("\n" + "🔐" * 25)
    print(" " * 15 + "Auth0 Configuration Test")
    print("🔐" * 25)
    
    results = []
    
    # Test dependencies
    results.append(("Dependencies", test_dependencies()))
    
    # Test auth helpers
    results.append(("Auth Helpers", test_auth_helpers()))
    
    # Test Auth0 config
    results.append(("Auth0 Config", test_auth0_config()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Auth0 is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print()


if __name__ == '__main__':
    main()
