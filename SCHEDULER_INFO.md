# Waitz Occupancy Auto-Update Scheduler

## Overview
SafeRoute now automatically fetches occupancy data from Waitz.io every 10 minutes.

## How It Works
- **Scheduler**: APScheduler (background task runner)
- **Update Frequency**: Every 10 minutes
- **What Gets Updated**: All buildings with `waitz_id` set in the database

## Setup

### Requirements
The scheduler is already configured. Just make sure `apscheduler` is installed:
```bash
pip install -r requirements.txt
```

### Starting the Scheduler
The scheduler starts automatically when you run:
```bash
python manage.py runserver
```

You'll see this message in the console:
```
Waitz occupancy scheduler started - will update every 10 minutes
```

## Configuration

### Change Update Frequency
Edit `accounts/scheduler.py`:
```python
scheduler.add_job(
    fetch_waitz_occupancy,
    'interval',
    minutes=10,  # Change this number (recommended: 5-15 minutes)
    ...
)
```

### Run Immediately on Startup
Uncomment this section in `accounts/scheduler.py`:
```python
# Run immediately on startup (optional)
scheduler.add_job(
    fetch_waitz_occupancy,
    'date',
    run_date=timezone.now(),
    id='fetch_waitz_occupancy_startup'
)
```

### Add Buildings for Auto-Update
To enable auto-updates for a building, set its `waitz_id`:

**Via Django Admin:**
1. Go to `/admin/accounts/building/`
2. Edit a building
3. Set the "Waitz ID" field (e.g., `clough-undergraduate-learning-commons`)

**Via Shell:**
```python
python manage.py shell
>>> from accounts.models import Building
>>> building = Building.objects.get(code='166')
>>> building.waitz_id = 'clough-undergraduate-learning-commons'
>>> building.save()
```

**Via Management Command:**
```bash
python manage.py fetch_waitz_occupancy --building-code 166 --waitz-id clough-undergraduate-learning-commons
```

## Manual Updates
You can still manually trigger updates:

```bash
# Update all buildings with waitz_id
python manage.py fetch_waitz_occupancy --all

# Update specific building
python manage.py fetch_waitz_occupancy --building-code 166 --waitz-id clough-undergraduate-learning-commons
```

## Monitoring

### Check Logs
The scheduler logs all updates:
- **Success**: `Scheduled Waitz occupancy update completed`
- **Error**: `Error in scheduled Waitz update: [error message]`

### Verify Updates
Check the database to see when occupancy was last updated:
```python
python manage.py shell
>>> from accounts.models import Building
>>> building = Building.objects.get(code='166')
>>> print(building.occupancy_last_updated)
```

## Important Notes

### Rate Limiting
- **Current**: Updates every 10 minutes = 144 requests/day
- **Respectful**: Won't overload Waitz.io servers
- **Safe**: Less likely to get IP blocked

### Waitz.io Terms of Service
- Waitz.io doesn't have a public API
- Current implementation uses web scraping
- Consider contacting Waitz for official API access
- For production, request permission or partnership

### Stopping the Scheduler
The scheduler stops when you:
1. Stop the Django development server (Ctrl+C)
2. Close the terminal

It will NOT run during:
- `python manage.py migrate`
- `python manage.py shell`
- `python manage.py makemigrations`
- Other management commands

## Troubleshooting

### Scheduler Not Running
Check that you're using `runserver`:
```bash
python manage.py runserver
```

Look for this message in console:
```
Background scheduler initialized
Waitz occupancy scheduler started - will update every 10 minutes
```

### Updates Not Working
1. Check that buildings have `waitz_id` set
2. Verify Waitz.io URLs are correct
3. Check logs for error messages
4. Test manually: `python manage.py fetch_waitz_occupancy --all`

### URL Format Issues
If you get 404 errors, the Waitz building slug might be wrong.

Check the actual Waitz.io URL format:
- Visit: https://waitz.io/gatech
- Click on a building
- Note the URL pattern
- Update the `waitz_id` accordingly

## Production Deployment

For production (Heroku, AWS, etc.), use:
- **Celery** with Redis/RabbitMQ (recommended)
- **Heroku Scheduler** (for Heroku)
- **AWS CloudWatch Events** (for AWS)
- **Cron jobs** (for traditional servers)

The current APScheduler setup is perfect for development and small deployments.

## Future Improvements

1. **Waitz API Integration**: Contact Waitz for official API access
2. **Caching**: Cache occupancy data to reduce database queries
3. **Webhooks**: If Waitz offers webhooks, use those instead
4. **Error Notifications**: Send alerts when updates fail
5. **Dashboard**: Admin page to monitor scheduler status

