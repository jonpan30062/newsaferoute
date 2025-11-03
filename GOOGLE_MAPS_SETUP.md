# Google Maps API Setup Guide

## Step-by-Step Instructions

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Create or Select a Project
- Click on the project dropdown at the top
- Click "New Project"
- Name it "SafeRoute" or similar
- Click "Create"

### 3. Enable Required APIs
Go to: https://console.cloud.google.com/apis/library

Enable these three APIs:
1. **Maps JavaScript API** - For displaying maps
2. **Directions API** - For calculating routes
3. **Geolocation API** - For user location

For each API:
- Search for the API name
- Click on it
- Click "Enable"

### 4. Create API Key
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Copy the API key that appears

### 5. Add API Key to SafeRoute
1. Open `saferoute/settings.py`
2. Find this line:
   ```python
   GOOGLE_MAPS_API_KEY = ""
   ```
3. Paste your API key between the quotes:
   ```python
   GOOGLE_MAPS_API_KEY = "AIzaSyC-YourActualAPIKeyHere"
   ```

### 6. (Optional but Recommended) Restrict Your API Key

For security, restrict your API key:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your API key
3. Under "Application restrictions":
   - For development: Select "None" or "HTTP referrers" with `localhost:8000`
   - For production: Select "HTTP referrers" and add your domain
4. Under "API restrictions":
   - Select "Restrict key"
   - Choose only the APIs you're using:
     * Maps JavaScript API
     * Directions API
     * Geolocation API
5. Click "Save"

### 7. Set Up Billing (Required)
Google Maps requires a billing account but provides $200 free credit per month.

1. Go to: https://console.cloud.google.com/billing
2. Click "Link a billing account"
3. Follow the instructions to add payment method
4. Enable billing for your project

**Note**: With $200 free credit monthly, typical development and small-scale use won't incur charges.

### 8. Test Your Setup
1. Restart your Django server:
   ```bash
   source venv/bin/activate
   python manage.py runserver
   ```
2. Visit: http://127.0.0.1:8000/map/
3. You should see the interactive map load
4. Try searching for "Engineering" or "ENG"
5. Click "Get Directions" to test routing

## Troubleshooting

### Map Not Loading
- Check browser console for errors
- Verify API key is correctly pasted in settings.py
- Ensure Maps JavaScript API is enabled
- Clear browser cache and reload

### Search Works But No Route
- Enable Directions API in Google Cloud Console
- Check that user location permission is granted in browser
- Verify billing is enabled on your Google Cloud account

### "This page can't load Google Maps correctly"
- Enable billing on your Google Cloud account
- Check API restrictions aren't too strict
- Verify all required APIs are enabled

## Cost Information

**Free Tier** (Monthly):
- $200 free credit = ~28,000 map loads or ~40,000 direction requests
- More than enough for development and small projects

**Typical Usage**:
- Development: Usually stays within free tier
- Production: Monitor usage in Google Cloud Console

## Security Best Practices

1. ✅ Never commit API keys to version control
2. ✅ Add `.env` file to `.gitignore` for production
3. ✅ Use environment variables in production
4. ✅ Restrict API key to specific domains
5. ✅ Set usage limits in Google Cloud Console
6. ✅ Monitor usage regularly

## Need Help?

- Google Maps API Documentation: https://developers.google.com/maps/documentation
- Google Cloud Console: https://console.cloud.google.com/
- API Key Best Practices: https://developers.google.com/maps/api-security-best-practices

