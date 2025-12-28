# Auth0 Authentication Flow Diagram

## 🔄 Complete Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FedAI Auth0 Flow                                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Browser    │         │  Flask App   │         │    Auth0     │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  1. Visit /            │                        │
       ├───────────────────────>│                        │
       │                        │                        │
       │  2. Check session      │                        │
       │     (no user)          │                        │
       │                        │                        │
       │  3. Redirect to /login │                        │
       │<───────────────────────┤                        │
       │                        │                        │
       │  4. Redirect to Auth0  │                        │
       │<───────────────────────┤                        │
       │                        │                        │
       │  5. Show login page    │                        │
       ├────────────────────────┼───────────────────────>│
       │                        │                        │
       │  6. User enters        │                        │
       │     credentials        │                        │
       ├────────────────────────┼───────────────────────>│
       │                        │                        │
       │                        │  7. Validate           │
       │                        │     credentials        │
       │                        │                        │
       │  8. Redirect to        │                        │
       │     /callback          │                        │
       │     (with code)        │                        │
       │<───────────────────────┼────────────────────────┤
       │                        │                        │
       │  9. Send code          │                        │
       ├───────────────────────>│                        │
       │                        │                        │
       │                        │  10. Exchange code     │
       │                        │      for token         │
       │                        ├───────────────────────>│
       │                        │                        │
       │                        │  11. Return token      │
       │                        │      + userinfo        │
       │                        │<───────────────────────┤
       │                        │                        │
       │                        │  12. Create session    │
       │                        │      (store userinfo)  │
       │                        │                        │
       │  13. Redirect to       │                        │
       │      dashboard         │                        │
       │<───────────────────────┤                        │
       │                        │                        │
       │  14. Access protected  │                        │
       │      resources         │                        │
       ├───────────────────────>│                        │
       │                        │                        │
       │                        │  15. Check session     │
       │                        │      (user exists)     │
       │                        │                        │
       │  16. Return dashboard  │                        │
       │      with user info    │                        │
       │<───────────────────────┤                        │
       │                        │                        │
```

---

## 🔐 Login Flow (Detailed)

```
User Action              Application                   Auth0
───────────              ───────────                   ─────

Visit site
    │
    ├──────────────────> Check if logged in
    │                    (session['user'] exists?)
    │                            │
    │                            NO
    │                            │
    │<─────────────────  Redirect to /login
    │
    ├──────────────────> Generate Auth0 URL
    │                    with callback URL
    │                            │
    │<─────────────────  Redirect to Auth0 ────────────>
    │                                                    │
    │                                            Show login page
    │                                                    │
Enter credentials ──────────────────────────────────────>
    │                                                    │
    │                                            Verify credentials
    │                                                    │
    │<───────────────────────────────────────── Redirect to callback
    │                                            (with auth code)
    │
    ├──────────────────> Receive auth code
    │                    Request access token ─────────>
    │                                                    │
    │                                            Exchange code
    │                                            for token
    │                                                    │
    │                    Receive token & userinfo <─────┤
    │                            │
    │                    Create Flask session
    │                    session['user'] = userinfo
    │                            │
    │<─────────────────  Redirect to dashboard
    │
Access dashboard
(authenticated)
```

---

## 🚪 Logout Flow

```
User Action              Application                   Auth0
───────────              ───────────                   ─────

Click logout
    │
    ├──────────────────> Clear Flask session
    │                    session.clear()
    │                            │
    │                    Generate Auth0 logout URL
    │                    with returnTo parameter
    │                            │
    │<─────────────────  Redirect to Auth0 logout ────>
    │                                                    │
    │                                            Clear Auth0 session
    │                                                    │
    │<───────────────────────────────────────── Redirect to returnTo
    │                                            (application home)
    │
Back at home page
(logged out)
```

---

## 🛡️ Protected Route Access

```
┌─────────────────────────────────────────────────┐
│           API Request to Protected Endpoint      │
└─────────────────────────────────────────────────┘

Request: POST /api/train
    │
    ├──> @login_required decorator
    │           │
    │    Check session['user']
    │           │
    │    ┌──────┴──────┐
    │    │             │
    │   YES            NO
    │    │             │
    │    ▼             ▼
    │ Continue    Return redirect
    │ to route    to /login
    │    │             │
    │    ▼             │
    │ Execute         │
    │ training        │
    │    │             │
    │    ▼             │
    │ Return          │
    │ success         │
    └────┴─────────────┘
```

---

## 📊 Session Management

```
┌──────────────────────────────────────┐
│         Session Lifecycle             │
└──────────────────────────────────────┘

Login
  │
  ├─> Create session
  │   session['user'] = {
  │     'name': 'John Doe',
  │     'email': 'john@example.com',
  │     'picture': 'https://...',
  │     'sub': 'auth0|123456'
  │   }
  │
  ├─> Set secure cookie
  │   (encrypted with SECRET_KEY)
  │
  ▼
Active Session
  │
  ├─> Subsequent requests
  │   include session cookie
  │
  ├─> Flask automatically
  │   decrypts and loads session
  │
  ├─> Routes access session['user']
  │
  ▼
Logout / Expiry
  │
  └─> session.clear()
      Cookie removed
```

---

## 🔄 Token Exchange (OAuth 2.0 Flow)

```
┌─────────────────────────────────────────────────────────┐
│            OAuth 2.0 Authorization Code Flow             │
└─────────────────────────────────────────────────────────┘

App                                                   Auth0
───                                                   ─────

1. Redirect user to Auth0
   GET /authorize
   ?client_id=xxx
   &redirect_uri=http://localhost:5000/callback
   &response_type=code
   &scope=openid profile email ─────────────────────>
                                                       │
                                                User authenticates
                                                       │
2. Redirect to callback                               │
   with authorization code    <───────────────────────┤
   GET /callback?code=abc123
   │
   │
3. Exchange code for token
   POST /oauth/token
   {
     grant_type: 'authorization_code',
     client_id: 'xxx',
     client_secret: 'yyy',
     code: 'abc123',
     redirect_uri: 'http://localhost:5000/callback'
   } ─────────────────────────────────────────────────>
                                                       │
                                                Verify code
                                                       │
4. Return access token & userinfo     <───────────────┤
   {
     access_token: 'token...',
     id_token: 'jwt...',
     userinfo: { name, email, ... }
   }
   │
   │
5. Store userinfo in session
   session['user'] = userinfo
   │
   │
6. Redirect to intended page
```

---

## 🎯 Development vs Production Flow

### Development Mode (No Auth0)

```
User visits /
    │
    ├──> Check AUTH0_ENABLED
    │          │
    │         NO (development mode)
    │          │
    ├──> Create mock session
    │    session['user'] = {
    │      'name': 'Developer',
    │      'email': 'dev@localhost'
    │    }
    │          │
    └──> Show dashboard
         (authenticated with mock user)
```

### Production Mode (With Auth0)

```
User visits /
    │
    ├──> Check AUTH0_ENABLED
    │          │
    │         YES (production mode)
    │          │
    ├──> Check session['user']
    │          │
    │      Not found
    │          │
    └──> Redirect to Auth0 login
         (full OAuth flow)
```

---

## 🔍 Error Handling Flow

```
┌────────────────────────────────────────┐
│         Error Scenarios                │
└────────────────────────────────────────┘

Callback Error
    │
    ├──> Try: authorize_access_token()
    │          │
    │    Exception raised
    │          │
    ├──> Log error
    │    add_log('Authentication error: ...')
    │          │
    └──> Redirect to /login
         (user tries again)

───────────────────────────────────────────

Invalid Session
    │
    ├──> @login_required check
    │          │
    │    session['user'] not found
    │          │
    ├──> Store intended URL
    │    session['next_url'] = request.url
    │          │
    └──> Redirect to /login
         (after login, redirect to next_url)
```

---

## 📱 Multi-Hospital Architecture

```
┌──────────────────────────────────────────────────────┐
│         Multiple Hospitals, One Auth0 Config          │
└──────────────────────────────────────────────────────┘

Auth0 Application
        │
        ├─────────────┬─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
  Hospital A    Hospital B    Hospital C    Central Server
  Port 5000     Port 5001     Port 5002     Port 8000
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
              Shared .env file
              Same Auth0 credentials
              Different callback ports
```

All hospitals share:

- Same AUTH0_DOMAIN
- Same AUTH0_CLIENT_ID
- Same AUTH0_CLIENT_SECRET
- Same SECRET_KEY

But have different:

- Callback URLs (different ports)
- Hospital IDs (A, B, C)
- Local data

---

## 🔐 Security Layers

```
┌────────────────────────────────────────┐
│         Security Architecture          │
└────────────────────────────────────────┘

1. HTTPS (Production)
   ├─> Encrypted communication
   └─> Prevents MITM attacks

2. OAuth 2.0 / OpenID Connect
   ├─> Industry standard
   └─> Secure token exchange

3. Flask Sessions
   ├─> Encrypted cookies
   ├─> SECRET_KEY based
   └─> HTTPOnly flag

4. Auth0 Security
   ├─> Multi-factor auth (optional)
   ├─> Anomaly detection
   ├─> Brute force protection
   └─> Session management

5. Route Protection
   ├─> @login_required decorator
   ├─> Session verification
   └─> Unauthorized redirect
```

---

## 📖 Related Documentation

- **AUTH0_SETUP.md** - Detailed setup instructions
- **AUTH0_QUICK_REFERENCE.md** - Quick start guide
- **AUTH0_INTEGRATION_SUMMARY.md** - Implementation details
- **MIGRATION_GUIDE.md** - Upgrade guide

---

**For implementation details, see the source code:**

- `hospital_interface.py` - Flask routes and Auth0 integration
- `utils/auth0_config.py` - Auth0 configuration
- `utils/auth.py` - Authentication helpers
