# Auth0 Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Auth0

```bash
python setup_auth0.py
```

Or manually create `.env`:

```env
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
SECRET_KEY=random-secret-key
```

### 3. Run Application

```bash
python hospital_interface.py --hospital A --port 5000
```

---

## 🔧 Auth0 Dashboard URLs

| Setting           | Value                                                                                                    |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| **Callback URLs** | `http://localhost:5000/callback`<br>`http://localhost:5001/callback`<br>`http://localhost:5002/callback` |
| **Logout URLs**   | `http://localhost:5000`<br>`http://localhost:5001`<br>`http://localhost:5002`                            |
| **Web Origins**   | Same as Logout URLs                                                                                      |

---

## 💻 Code Examples

### Protect a Route

```python
from utils.auth import login_required

@app.route('/my-route')
@login_required
def my_protected_route():
    return "This requires authentication"
```

### Get User Info

```python
from utils.auth import get_user_info

user = get_user_info()
print(f"Logged in as: {user['name']}")
print(f"Email: {user['email']}")
```

### Check Authentication

```python
from utils.auth import is_authenticated

if is_authenticated():
    print("User is logged in")
else:
    print("User is not logged in")
```

### In Templates

```html
{% if user %}
<p>Welcome, {{ user.name }}!</p>
<a href="{{ url_for('logout') }}">Logout</a>
{% else %}
<a href="{{ url_for('login') }}">Login</a>
{% endif %}
```

---

## 🔍 Troubleshooting

| Problem                         | Solution                                          |
| ------------------------------- | ------------------------------------------------- |
| **Missing Auth0 configuration** | Run `python setup_auth0.py` or create `.env` file |
| **Callback mismatch**           | Add callback URLs in Auth0 dashboard              |
| **Invalid state**               | Clear cookies and try again                       |
| **Login loop**                  | Check allowed callback URLs match your port       |

---

## 📊 Application Routes

| Route                  | Auth Required | Purpose                  |
| ---------------------- | ------------- | ------------------------ |
| `/`                    | ✅ Yes        | Hospital dashboard       |
| `/login`               | ❌ No         | Redirect to Auth0 login  |
| `/callback`            | ❌ No         | Handle Auth0 callback    |
| `/logout`              | ❌ No         | Logout and clear session |
| `/api/download-global` | ✅ Yes        | Download global model    |
| `/api/train`           | ✅ Yes        | Start training           |
| `/api/push-global`     | ✅ Yes        | Push weights to server   |
| `/api/state`           | ❌ No         | Get hospital state       |
| `/api/events`          | ❌ No         | Server-sent events       |

---

## 🔐 Environment Variables

| Variable              | Required | Description                   |
| --------------------- | -------- | ----------------------------- |
| `AUTH0_DOMAIN`        | Yes      | Your Auth0 tenant domain      |
| `AUTH0_CLIENT_ID`     | Yes      | Application client ID         |
| `AUTH0_CLIENT_SECRET` | Yes      | Application client secret     |
| `SECRET_KEY`          | Yes      | Flask session secret key      |
| `HOSPITAL_ID`         | No       | Hospital identifier (A, B, C) |

Generate `SECRET_KEY`:

```bash
python -c "import os; print(os.urandom(24).hex())"
```

---

## 🏥 Multi-Hospital Setup

Run multiple hospitals on different ports:

**Terminal 1:**

```bash
python hospital_interface.py --hospital A --port 5000
```

**Terminal 2:**

```bash
python hospital_interface.py --hospital B --port 5001
```

**Terminal 3:**

```bash
python hospital_interface.py --hospital C --port 5002
```

Each hospital shares the same Auth0 configuration but runs independently.

---

## 📖 Documentation Files

- **AUTH0_SETUP.md** - Complete setup guide
- **AUTH0_INTEGRATION_SUMMARY.md** - Technical implementation details
- **.env.example** - Configuration template
- **README.md** - Project overview

---

## 🆘 Getting Help

1. Check **AUTH0_SETUP.md** for detailed instructions
2. Verify `.env` file configuration
3. Check Auth0 dashboard settings match required URLs
4. Review browser console for JavaScript errors
5. Check Flask terminal output for errors

---

## ⚡ Common Commands

```bash
# Setup Auth0
python setup_auth0.py

# Install dependencies
pip install -r requirements.txt

# Generate secret key
python -c "import os; print(os.urandom(24).hex())"

# Run hospital A
python hospital_interface.py --hospital A --port 5000

# Run central server
python server/server.py

# View help
python hospital_interface.py --help
```

---

**For detailed information, see [AUTH0_SETUP.md](AUTH0_SETUP.md)**
