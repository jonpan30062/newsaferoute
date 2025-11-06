# Troubleshooting: Safety Concerns Not Visible in Admin

## Verification Steps

### Step 1: Confirm Server is Running
```bash
# Check if server is running
ps aux | grep "manage.py runserver"
```

### Step 2: Restart the Server
The server may need to be restarted to pick up admin changes:
```bash
# Stop the current server (Ctrl+C in terminal where it's running)
# Then restart:
python3 manage.py runserver
```

### Step 3: Clear Browser Cache
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
- Or clear browser cache for localhost

### Step 4: Access Admin Panel
1. Go to: **http://127.0.0.1:8000/admin/**
2. Login with:
   - Email: `admin@saferoute.com`
   - Password: `admin123`

### Step 5: Look for "Safety Concerns"
- Should appear under **ACCOUNTS** section
- Look for: **"Safety Concerns"** (plural)
- NOT "Safety Concern" (singular)

### Step 6: Verify Registration
Run this command to verify:
```bash
python3 manage.py shell
```
Then in the shell:
```python
from django.contrib import admin
from accounts.models import SafetyConcern
print(SafetyConcern in admin.site._registry)  # Should print True
```

## Expected Location in Admin Panel

```
Django Administration
├── ACCOUNTS
│   ├── Users
│   ├── Buildings
│   ├── Favorites
│   ├── Saved Routes
│   ├── Safety Alerts      ← Existing feature
│   └── Safety Concerns    ← NEW! Should be here
├── AUTHENTICATION AND AUTHORIZATION
│   ├── Groups
│   └── Users
```

## Common Issues

### Issue 1: Not seeing it after login
**Solution**: Look under **ACCOUNTS** section, not at the top

### Issue 2: Server hasn't reloaded
**Solution**: Restart the Django server:
```bash
# Kill existing server
pkill -f "manage.py runserver"
# Start new one
python3 manage.py runserver
```

### Issue 3: Model not migrated
**Solution**: Run migrations:
```bash
python3 manage.py migrate
```

### Issue 4: Admin.py not being loaded
**Solution**: Check if there are syntax errors:
```bash
python3 manage.py check
```

## Quick Test

1. **Restart server** (important!)
2. **Clear browser cache** or use incognito/private window
3. **Login to admin**: http://127.0.0.1:8000/admin/
4. **Scroll down** to ACCOUNTS section
5. **Look for "Safety Concerns"**

## If Still Not Visible

Run this diagnostic:
```bash
python3 manage.py shell << 'EOF'
from django.contrib import admin
from accounts.models import SafetyConcern

print("=== Admin Registration Check ===")
print(f"Registered: {SafetyConcern in admin.site._registry}")
print(f"App label: {SafetyConcern._meta.app_label}")
print(f"Verbose name: {SafetyConcern._meta.verbose_name_plural}")

# List all registered models
print("\n=== All Registered Models ===")
for model in admin.site._registry.keys():
    print(f"  - {model._meta.app_label}.{model.__name__}")
EOF
```

This should show "Safety Concerns" in the list.

