# Troubleshooting: Same Code, Different Behavior

If your version functions differently than others despite the same git commit, check these common issues:

## 1. Database State Differences

**Problem**: SQLite database (`db.sqlite3`) is not in git, so each user has different data.

**Solution**: 
```bash
# Delete existing database and recreate
rm db.sqlite3
python manage.py migrate
python manage.py import_gt_buildings
python manage.py populate_alerts
```

## 2. Missing Migrations

**Problem**: Database schema might be out of sync.

**Check**:
```bash
python manage.py showmigrations accounts
```

**Solution**:
```bash
python manage.py migrate
```

## 3. Missing Dependencies

**Problem**: Different package versions or missing packages.

**Check**:
```bash
pip list | grep -E "(Django|pandas|openpyxl|Pillow|requests)"
```

**Solution**:
```bash
pip install -r requirements.txt
```

## 4. Environment Variables

**Problem**: Different API keys or settings.

**Check**: 
- Look for `.env` file (not in git)
- Check `saferoute/settings.py` for hardcoded values

**Solution**:
- Create `.env` file from `.env.example`
- Set `GOOGLE_MAPS_API_KEY` in `.env` or `settings.py`

## 5. Python/Django Version Differences

**Check**:
```bash
python --version
python manage.py --version
```

**Solution**: Use same Python version (3.12+) and Django (5.0)

## 6. Static Files / Cache

**Problem**: Old cached files or static files not updated.

**Solution**:
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Collect static files (if using static files)
python manage.py collectstatic --noinput
```

## 7. Browser Cache

**Problem**: Old JavaScript/CSS cached in browser.

**Solution**: 
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Clear browser cache
- Try incognito/private mode

## 8. Database Data Verification

**Check current state**:
```bash
python manage.py shell -c "
from accounts.models import Building, SafetyAlert;
print(f'Buildings: {Building.objects.count()}');
print(f'Safety Alerts: {SafetyAlert.objects.count()}');
print(f'Circle Alerts: {SafetyAlert.objects.filter(location_type=\"circle\").count()}');
"
```

**Expected**:
- Buildings: 81
- Circle alerts should have radius: 76.2m (250ft)

## 9. Common Issues

### Issue: Circle alerts showing as point markers
**Cause**: Old alerts created before code update
**Fix**: Re-run `python manage.py populate_alerts` or update existing alerts in admin

### Issue: Buildings not searchable
**Cause**: Database not populated
**Fix**: Run `python manage.py import_gt_buildings`

### Issue: Map not loading
**Cause**: Missing or invalid Google Maps API key
**Fix**: Check `GOOGLE_MAPS_API_KEY` in settings.py

### Issue: Search not working
**Cause**: No buildings in database
**Fix**: Run `python manage.py import_gt_buildings`

## Quick Reset (Nuclear Option)

If nothing else works, completely reset your environment:

```bash
# 1. Delete database
rm db.sqlite3

# 2. Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 3. Reinstall dependencies
pip install -r requirements.txt --upgrade

# 4. Run migrations
python manage.py migrate

# 5. Populate data
python manage.py import_gt_buildings
python manage.py populate_alerts

# 6. Create superuser (if needed)
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

## Still Having Issues?

1. Check git status: `git status` (should be clean)
2. Verify commit: `git log -1` (should match others)
3. Compare Python version: `python --version`
4. Compare Django version: `python manage.py --version`
5. Check for uncommitted changes: `git diff`

