# Auth0 Integration Guide

This project now includes Auth0 authentication to secure the federated learning hospital interfaces.

## 🔐 Features Added

- **User Authentication**: Secure login/logout using Auth0
- **Protected Routes**: All training and model management endpoints require authentication
- **User Profile Display**: Shows logged-in user information in the dashboard header
- **Session Management**: Secure session handling with Flask sessions
- **Development Mode**: Can run without Auth0 for local development

## 📋 Prerequisites

1. An Auth0 account (free tier available at [auth0.com](https://auth0.com))
2. Python 3.8+ with pip
3. All project dependencies installed

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the new Auth0 dependencies:

- `authlib>=1.3.0` - OAuth/OIDC library
- `python-dotenv>=1.0.0` - Environment variable management

### Step 2: Create Auth0 Application

1. **Sign up/Login to Auth0**

   - Go to [auth0.com](https://auth0.com)
   - Create a free account or login

2. **Create a New Application**

   - Navigate to Applications → Applications
   - Click "Create Application"
   - Name: "FedAI Hospital Interface" (or any name you prefer)
   - Type: Select "Regular Web Applications"
   - Click "Create"

3. **Configure Application Settings**

   In your Auth0 application settings, configure:

   **Allowed Callback URLs:**

   ```
   http://localhost:5000/callback,
   http://localhost:5001/callback,
   http://localhost:5002/callback
   ```

   **Allowed Logout URLs:**

   ```
   http://localhost:5000,
   http://localhost:5001,
   http://localhost:5002
   ```

   **Allowed Web Origins:**

   ```
   http://localhost:5000,
   http://localhost:5001,
   http://localhost:5002
   ```

4. **Save Your Credentials**
   - Domain (e.g., `dev-abc123.us.auth0.com`)
   - Client ID
   - Client Secret

### Step 3: Configure Environment Variables

1. **Copy the example file:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your Auth0 credentials:**

   ```env
   AUTH0_DOMAIN=your-auth0-domain.auth0.com
   AUTH0_CLIENT_ID=your-client-id-here
   AUTH0_CLIENT_SECRET=your-client-secret-here
   SECRET_KEY=your-secret-key-here
   ```

3. **Generate a SECRET_KEY:**
   ```bash
   python -c "import os; print(os.urandom(24).hex())"
   ```
   Copy the output and use it as your SECRET_KEY

### Step 4: Run the Application

Start each hospital interface as usual:

```bash
# Hospital A on port 5000
python hospital_interface.py --hospital A --port 5000

# Hospital B on port 5001
python hospital_interface.py --hospital B --port 5001

# Hospital C on port 5002
python hospital_interface.py --hospital C --port 5002
```

## 🔒 Authentication Flow

1. **First Visit**: Users are redirected to Auth0 login page
2. **Login**: Users authenticate with Auth0 (email/password, social login, etc.)
3. **Callback**: Auth0 redirects back to the application with authentication token
4. **Session**: User session is created and maintained
5. **Protected Access**: All training operations require authenticated session
6. **Logout**: Clears session and redirects to Auth0 logout

## 🎨 UI Changes

The hospital dashboard now includes:

- **User Profile Section**: Displays user avatar, name, and email in the header
- **Logout Button**: Secure logout functionality
- **Protected Actions**: Download, Train, and Push operations require authentication

## 🛠️ Development Mode

If Auth0 is not configured (missing `.env` file), the application runs in development mode:

- ⚠️ **Warning displayed**: "Auth0 not configured"
- 🔓 **No authentication required**: All routes are accessible
- 👤 **Mock session created**: Developer session for testing

**Note:** Development mode should NEVER be used in production!

## 📁 New Files Added

```
utils/
  ├── auth0_config.py    # Auth0 configuration management
  └── auth.py            # Authentication decorators and helpers
.env.example             # Template for environment variables
AUTH0_SETUP.md          # This guide
```

## 🔧 Configuration Files

### utils/auth0_config.py

Manages Auth0 settings and validates configuration

### utils/auth.py

Provides:

- `@login_required` decorator for protecting routes
- `get_current_user()` - Get logged-in user info
- `is_authenticated()` - Check authentication status
- `get_user_info()` - Get detailed user information

## 🎯 Usage Examples

### Protecting Custom Routes

```python
from utils.auth import login_required, get_user_info

@app.route('/my-custom-route')
@login_required
def my_route():
    user = get_user_info()
    return f"Hello {user['name']}!"
```

### Checking Authentication in Templates

```html
{% if user %}
<p>Welcome, {{ user.name }}!</p>
{% else %}
<a href="{{ url_for('login') }}">Login</a>
{% endif %}
```

## 🐛 Troubleshooting

### "Missing required Auth0 configuration" Error

- Ensure `.env` file exists in project root
- Verify all required variables are set (AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET)

### "Callback URL mismatch" Error

- Check that callback URLs in Auth0 dashboard match your application ports
- Format: `http://localhost:PORT/callback`

### "Invalid state parameter" Error

- Clear browser cookies and try again
- Ensure SECRET_KEY is set and consistent

### Login Redirect Loop

- Verify Allowed Callback URLs in Auth0 settings
- Check that the domain in `.env` matches Auth0 application domain

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use strong SECRET_KEY** - Generate random, long keys
3. **HTTPS in Production** - Always use HTTPS for production deployments
4. **Rotate Secrets** - Periodically rotate Auth0 client secrets
5. **Monitor Access** - Use Auth0 logs to monitor authentication attempts

## 📚 Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 Python Quickstart](https://auth0.com/docs/quickstart/webapp/python)
- [Authlib Documentation](https://docs.authlib.org/)
- [Flask Session Documentation](https://flask.palletsprojects.com/en/3.0.x/quickstart/#sessions)

## 🆘 Support

For Auth0-specific issues, refer to:

- [Auth0 Community](https://community.auth0.com/)
- [Auth0 Support](https://support.auth0.com/)

For application-specific issues, check the main README.md or project documentation.
