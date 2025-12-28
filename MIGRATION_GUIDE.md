# Migration Guide: Adding Auth0 to Existing FedAI Deployment

## 📋 Overview

This guide helps you add Auth0 authentication to an existing FedAI installation without disrupting current operations.

## ⚠️ Before You Start

**Backup your data:**

```bash
# Backup checkpoints and data
cp -r checkpoints checkpoints_backup
cp -r data data_backup
```

**Check current status:**

```bash
# Ensure no training is running
# Stop all hospital interfaces
# Stop central server
```

## 🔄 Migration Steps

### Step 1: Update Dependencies

```bash
# Pull latest code or update requirements.txt
pip install -r requirements.txt

# Verify new packages installed
python -c "import authlib; import dotenv; print('✅ Dependencies installed')"
```

### Step 2: Configure Auth0

**Option A: Interactive Setup (Recommended)**

```bash
python setup_auth0.py
```

**Option B: Manual Setup**

```bash
# Copy template
cp .env.example .env

# Edit .env with your Auth0 credentials
nano .env  # or use your preferred editor
```

### Step 3: Update Auth0 Dashboard

Add these URLs to your Auth0 application settings:

**Allowed Callback URLs:**

```
http://localhost:5000/callback
http://localhost:5001/callback
http://localhost:5002/callback
https://your-domain.com/callback  # If using custom domain
```

**Allowed Logout URLs:**

```
http://localhost:5000
http://localhost:5001
http://localhost:5002
https://your-domain.com  # If using custom domain
```

**Allowed Web Origins:**

```
http://localhost:5000
http://localhost:5001
http://localhost:5002
https://your-domain.com  # If using custom domain
```

### Step 4: Test Configuration

```bash
# Run test script
python test_auth0.py

# Should show all green checkmarks
```

### Step 5: Restart Services

```bash
# Start central server
python server/server.py

# Start hospital A with auth
python hospital_interface.py --hospital A --port 5000

# Test in browser - should redirect to login
```

## 🔍 Verification Checklist

- [ ] Dependencies installed (`authlib`, `python-dotenv`)
- [ ] `.env` file created with Auth0 credentials
- [ ] Auth0 dashboard callback URLs configured
- [ ] Test script passes all checks
- [ ] Can access login page
- [ ] Can login successfully
- [ ] User profile appears in dashboard
- [ ] Can perform training operations
- [ ] Can logout successfully

## 🚨 Troubleshooting Migration Issues

### Issue: "Missing Auth0 configuration" Warning

**Cause:** `.env` file not found or incomplete

**Solution:**

```bash
python setup_auth0.py
```

### Issue: "Callback URL mismatch"

**Cause:** Auth0 dashboard URLs not configured

**Solution:**

- Login to Auth0 dashboard
- Go to Applications → Your App → Settings
- Add callback URLs listed in Step 3
- Save changes

### Issue: Users Can't Login

**Cause:** Multiple possible causes

**Solution:**

1. Clear browser cookies
2. Check `.env` file has correct credentials
3. Verify Auth0 domain format (no `https://` prefix)
4. Check Auth0 application is enabled

### Issue: Session Issues After Migration

**Cause:** Secret key changed

**Solution:**

- All users need to re-login once after migration
- This is normal and expected

## 🔄 Rollback Procedure

If you need to rollback to pre-Auth0 version:

### Option 1: Disable Auth0 (Temporary)

```bash
# Rename .env to disable Auth0
mv .env .env.disabled

# Application runs in development mode (no auth required)
# ⚠️ WARNING: Do not use in production!
```

### Option 2: Full Rollback

```bash
# Restore previous version
git checkout <previous-commit>

# Reinstall old dependencies
pip install -r requirements.txt

# Restore data
rm -rf checkpoints
mv checkpoints_backup checkpoints
```

## 📊 Post-Migration Monitoring

### Check Authentication Logs

Auth0 provides detailed logs:

1. Login to Auth0 dashboard
2. Go to Monitoring → Logs
3. Filter by your application
4. Check for successful logins

### Monitor Application Logs

Check for auth-related messages:

```bash
# When starting hospital interface, look for:
[INFO] Auth0 authentication enabled

# Or if not configured:
[WARNING] Auth0 not configured: ...
[WARNING] Running without authentication (development mode only!)
```

## 🎯 Best Practices After Migration

### 1. User Onboarding

- Inform users about new login requirement
- Provide Auth0 credentials or setup self-registration
- Share login URL: `http://localhost:5000` (or your domain)

### 2. Security Hardening

```bash
# Ensure .env is not committed
git status  # Should not show .env

# Verify .gitignore includes .env
cat .gitignore | grep .env
```

### 3. Production Considerations

**If deploying to production:**

```env
# Update .env with production URLs
AUTH0_DOMAIN=your-production-domain.auth0.com
# Update callback URLs to use HTTPS
```

**In Auth0 dashboard:**

- Use production domain in callback URLs
- Enable HTTPS only
- Configure MFA (Multi-Factor Authentication)
- Set up proper user roles

### 4. Backup Auth0 Configuration

Save your `.env` template (without secrets):

```bash
# Create sanitized backup
cat .env | sed 's/=.*/=REDACTED/' > .env.template.backup
```

## 📈 Feature Enhancements (Optional)

Now that Auth0 is integrated, you can enable:

### Social Login

- Configure Google, GitHub, etc. in Auth0
- No code changes needed

### Multi-Factor Authentication

- Enable in Auth0 dashboard
- Adds extra security layer

### Role-Based Access Control

```python
# Add role checking to routes
@app.route('/admin')
@login_required
def admin_route():
    user = get_user_info()
    if 'admin' not in user.get('roles', []):
        return "Unauthorized", 403
    return "Admin panel"
```

## ✅ Migration Complete!

Once all checks pass and services are running:

1. ✅ Auth0 authentication active
2. ✅ All users can login
3. ✅ Hospital interfaces protected
4. ✅ Training operations secure
5. ✅ Logs show authentication activity

## 📚 Additional Resources

- [AUTH0_SETUP.md](AUTH0_SETUP.md) - Detailed setup guide
- [AUTH0_QUICK_REFERENCE.md](AUTH0_QUICK_REFERENCE.md) - Quick commands
- [Auth0 Docs](https://auth0.com/docs) - Official documentation

## 🆘 Support

If you encounter issues during migration:

1. Run `python test_auth0.py` for diagnostics
2. Check application logs for error messages
3. Review Auth0 dashboard logs
4. Refer to troubleshooting section above
5. Check AUTH0_SETUP.md for detailed solutions

---

**Migration Date:** ******\_******

**Performed By:** ******\_******

**Notes:** ******\_******
