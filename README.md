# SafeRoute - Campus Navigation System

SafeRoute is a Django web application that helps students navigate campus buildings with integrated Google Maps routing.

## Features

✅ **User Authentication**
- Email-based registration and login
- Custom user profiles with full name
- Secure password validation (8+ chars, 1 number required)

✅ **Building Search**
- Search by building name or code (partial matching)
- Real-time search suggestions
- 10 pre-populated campus buildings

✅ **Interactive Map**
- Google Maps integration
- Real-time user location tracking
- Building markers and information

✅ **Route Planning**
- Calculate fastest walking routes
- Dynamic route updates based on user location
- Distance and duration display
- Turn-by-turn directions

## Setup Instructions

### 1. Install Dependencies

```bash
cd /Users/victorhuang/Desktop/saferoute/saferoute
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Google Maps API

1. Go to [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
2. Create a new project or select existing one
3. Enable these APIs:
   - Maps JavaScript API
   - Directions API
   - Geolocation API
4. Create credentials (API Key)
5. Add the API key to `saferoute/settings.py`:

```python
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"
```

**Important Security Notes:**
- Restrict your API key to your domain in production
- Set usage limits to prevent abuse
- Never commit API keys to version control

### 3. Database Setup

```bash
python manage.py migrate
python manage.py populate_buildings
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Application Routes

- `/` - Home page
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/dashboard/` - User dashboard (requires login)
- `/map/` - Interactive campus map
- `/admin/` - Django admin panel
- `/api/buildings/search/` - Building search API endpoint

## User Story Implementation

**As a student, I want to search for a building on campus so I can view the fastest walking route on the map.**

### Features Implemented:

1. ✅ **Search Bar** - Search by partial name or building code
   - Example: "ENG" or "Engineering"
   - Case-insensitive partial matching
   - Real-time search results dropdown

2. ✅ **Map Display** - Shows selected building location
   - Google Maps integration
   - Building markers
   - User location marker

3. ✅ **Route Calculation** - Fastest walking route
   - Google Directions API integration
   - Walking mode optimization
   - Visual route on map

4. ✅ **Dynamic Updates** - Route recalculates on location change
   - Real-time location tracking
   - Automatic route updates
   - Distance and duration display

5. ✅ **Clear "Get Directions" Button**
   - Prominent button in UI
   - Shows route information
   - Clear route option

## Sample Buildings

The system includes 10 pre-populated buildings:

1. Student Union Building (SUB)
2. Engineering Building (ENG)
3. Science Hall (SCI)
4. Library and Learning Center (LIB)
5. Business Administration Building (BUS)
6. Recreation Center (REC)
7. Arts and Humanities Building (ART)
8. Medical Sciences Building (MED)
9. Computer Science Building (CS)
10. Residence Hall North (RHN)

## Technology Stack

- **Backend**: Django 5.2.7
- **Database**: SQLite
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Maps**: Google Maps JavaScript API
- **Routing**: Google Directions API

## Project Structure

```
saferoute/
├── accounts/              # Main application
│   ├── migrations/       # Database migrations
│   ├── management/       # Custom management commands
│   ├── templates/        # HTML templates
│   ├── models.py         # User & Building models
│   ├── views.py          # View functions & API endpoints
│   ├── forms.py          # Authentication forms
│   ├── urls.py           # URL routing
│   └── admin.py          # Admin configuration
├── saferoute/            # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI configuration
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Building Search API

**Endpoint**: `/api/buildings/search/`

**Method**: GET

**Parameters**:
- `q` (optional): Search query (building name or code)

**Response**:
```json
{
  "success": true,
  "count": 2,
  "buildings": [
    {
      "id": 1,
      "name": "Engineering Building",
      "code": "ENG",
      "address": "456 Tech Way, Campus, CA 94000",
      "latitude": 37.874730,
      "longitude": -122.257990,
      "description": "Engineering classrooms and labs"
    }
  ]
}
```

## Future Enhancements

- Save favorite buildings
- Route history
- Multiple route options (fastest, scenic, accessible)
- Building hours and amenities
- Indoor navigation
- Public transit integration
- Social features (share routes)

## Development

### Add New Buildings

```bash
python manage.py shell
```

```python
from accounts.models import Building

Building.objects.create(
    name="New Building",
    code="NEW",
    address="123 Campus St",
    latitude=37.871899,
    longitude=-122.258537,
    description="Building description"
)
```

### Run Tests

```bash
python manage.py test
```

## Support

For issues or questions, please contact the development team.

## License

MIT License - See LICENSE file for details

