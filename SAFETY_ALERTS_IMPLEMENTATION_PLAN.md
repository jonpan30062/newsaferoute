# Safety Alerts Feature - Implementation Plan

## Overview
This document outlines the complete implementation plan for adding safety alerts to the SafeRoute application. The feature will allow admins to create safety alerts (construction, emergencies, etc.) that appear on the map as icons/colored zones with detailed information in popups.

---

## 1. Database Model Design

### 1.1 SafetyAlert Model
**Location:** `accounts/models.py`

**Fields:**
- `id` (BigAutoField) - Primary key
- `title` (CharField, max_length=255) - Short alert title (e.g., "Construction Zone")
- `description` (TextField) - Detailed description of the alert
- `alert_type` (CharField with choices) - Type of alert:
  - 'construction' - Construction/road work
  - 'emergency' - Emergency situation
  - 'maintenance' - Maintenance work
  - 'hazard' - General hazard
  - 'other' - Other safety concern
- `severity` (CharField with choices) - Severity level:
  - 'low' - Low priority (yellow)
  - 'medium' - Medium priority (orange)
  - 'high' - High priority (red)
  - 'critical' - Critical (dark red)
- `location_type` (CharField with choices) - How the alert is displayed:
  - 'point' - Single point marker (icon)
  - 'circle' - Circular zone (colored overlay)
  - 'polygon' - Polygon zone (colored overlay)
- `latitude` (DecimalField, max_digits=9, decimal_places=6) - Center point lat
- `longitude` (DecimalField, max_digits=9, decimal_places=6) - Center point lng
- `radius` (DecimalField, max_digits=10, decimal_places=2, null=True, blank=True) - Radius in meters for circle zones
- `polygon_coordinates` (TextField, null=True, blank=True) - JSON string of polygon coordinates for polygon zones
- `is_active` (BooleanField, default=True) - Whether alert is currently active
- `start_date` (DateTimeField, null=True, blank=True) - When alert becomes active
- `end_date` (DateTimeField, null=True, blank=True) - When alert expires
- `created_by` (ForeignKey to User) - Admin who created the alert
- `created_at` (DateTimeField, auto_now_add=True) - Creation timestamp
- `updated_at` (DateTimeField, auto_now=True) - Last update timestamp

**Meta Options:**
- `verbose_name`: "Safety Alert"
- `verbose_name_plural`: "Safety Alerts"
- `ordering`: ['-severity', '-created_at']
- `indexes`: On `is_active`, `alert_type`, `severity`, `created_at`

**Methods:**
- `__str__()` - Return formatted string: "{title} ({alert_type})"
- `is_currently_active()` - Check if alert is active based on dates and is_active flag
- `get_icon_url()` - Return appropriate marker icon based on alert_type and severity
- `get_color()` - Return hex color code based on severity
- `get_polygon_coordinates()` - Parse and return polygon coordinates as list (if polygon type)

**Validation:**
- Ensure radius is provided if location_type is 'circle'
- Ensure polygon_coordinates is provided if location_type is 'polygon'
- Ensure end_date is after start_date if both are provided
- Ensure latitude/longitude are within valid ranges

---

## 2. Database Migration

### 2.1 Create Migration
**File:** `accounts/migrations/0005_safetyalert.py`

**Steps:**
1. Create model with all fields
2. Add indexes for performance
3. Set up foreign key relationship to User model
4. Add any constraints or validation

**Dependencies:**
- `0004_savedroute`

---

## 3. Admin Interface

### 3.1 SafetyAlertAdmin Class
**Location:** `accounts/admin.py`

**Features:**
- List display: `title`, `alert_type`, `severity`, `location_type`, `is_active`, `created_at`, `created_by`
- List filters: `alert_type`, `severity`, `is_active`, `created_at`, `created_by`
- Search fields: `title`, `description`
- Date hierarchy: `created_at`
- Readonly fields: `created_at`, `updated_at`
- Autocomplete: `created_by`

**Custom Admin Actions:**
- "Activate selected alerts"
- "Deactivate selected alerts"
- "Mark as expired"

**Form Customization:**
- Use widgets for better UX:
  - Textarea for description
  - Date/time pickers for start_date/end_date
  - JSON field widget for polygon_coordinates (with validation)
- Add help text for complex fields (polygon_coordinates format)

**Inline Admin:**
- Consider adding related model for alert history/updates if needed in future

---

## 4. API Endpoints

### 4.1 Get All Active Alerts
**URL:** `/api/alerts/`
**Method:** GET
**Authentication:** Not required (public safety information)
**Query Parameters:**
- `alert_type` (optional) - Filter by type
- `severity` (optional) - Filter by severity
- `bounds` (optional) - Filter by map bounds (north, south, east, west)

**Response Format:**
```json
{
  "success": true,
  "count": 2,
  "alerts": [
    {
      "id": 1,
      "title": "Construction Zone",
      "description": "Road construction on Main Street",
      "alert_type": "construction",
      "severity": "medium",
      "location_type": "circle",
      "latitude": 37.871899,
      "longitude": -122.258537,
      "radius": 100.0,
      "polygon_coordinates": null,
      "is_active": true,
      "start_date": "2025-01-15T08:00:00Z",
      "end_date": "2025-02-15T18:00:00Z",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z",
      "icon_url": "/static/icons/construction-medium.png",
      "color": "#f59e0b"
    }
  ]
}
```

**Implementation:**
- Filter by `is_currently_active()` method
- Only return alerts that are currently active
- Support optional filtering by type/severity
- Support optional bounding box filtering for map viewport

### 4.2 Get Single Alert Details
**URL:** `/api/alerts/<id>/`
**Method:** GET
**Authentication:** Not required

**Response:** Single alert object with full details

---

## 5. Frontend Implementation

### 5.1 Map Integration
**Location:** `accounts/templates/accounts/map.html`

**Global Variables to Add:**
```javascript
let safetyAlerts = [];
let alertMarkers = [];
let alertCircles = [];
let alertPolygons = [];
let alertInfoWindows = [];
```

### 5.2 Alert Display Functions

#### 5.2.1 Load Alerts Function
- Fetch alerts from API on map initialization
- Call `loadAlerts()` after map is initialized
- Handle errors gracefully

#### 5.2.2 Display Point Alerts
- Create Google Maps Marker for each point alert
- Use custom icon based on alert_type and severity
- Set click handler to open info window
- Store marker reference in `alertMarkers` array

#### 5.2.3 Display Circle Alerts
- Create Google Maps Circle overlay
- Set center from latitude/longitude
- Set radius from radius field (convert meters to appropriate units)
- Set fill/stroke colors based on severity
- Set click handler to open info window
- Store circle reference in `alertCircles` array

#### 5.2.4 Display Polygon Alerts
- Parse polygon_coordinates JSON
- Create Google Maps Polygon overlay
- Set fill/stroke colors based on severity
- Set click handler to open info window
- Store polygon reference in `alertPolygons` array

#### 5.2.5 Info Window Creation
- Create Google Maps InfoWindow for each alert
- Include: title, description, alert type, severity, timestamp
- Format timestamp nicely (e.g., "Posted 2 hours ago")
- Style with appropriate colors based on severity
- Ensure only one info window is open at a time

### 5.3 Custom Icons
**Icon Design:**
- Different icons for each alert_type:
  - Construction: Construction cone icon
  - Emergency: Warning triangle/alert icon
  - Maintenance: Wrench/tool icon
  - Hazard: Exclamation icon
  - Other: Generic alert icon
- Color variations based on severity:
  - Low: Yellow (#fbbf24)
  - Medium: Orange (#f59e0b)
  - High: Red (#ef4444)
  - Critical: Dark Red (#dc2626)

**Options:**
1. Use Google Maps built-in icons with custom colors
2. Use SVG icons (can be defined inline or as static files)
3. Use external icon library (Font Awesome, Bootstrap Icons)

**Recommendation:** Use Bootstrap Icons (already in use) with custom colored markers

### 5.4 Dynamic Updates

#### 5.4.1 Polling Mechanism
- Set up interval to check for new alerts (e.g., every 30 seconds)
- Fetch alerts API on interval
- Compare with existing alerts
- Add new alerts, update changed alerts, remove expired alerts
- Use efficient update mechanism (don't reload all alerts if nothing changed)

#### 5.4.2 Update Logic
```javascript
function updateAlerts() {
  fetch('/api/alerts/')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const newAlerts = data.alerts;
        // Compare with existing alerts
        // Add/update/remove as needed
        refreshAlertDisplay(newAlerts);
      }
    });
}
```

#### 5.4.3 Efficient Refresh
- Track alert IDs currently displayed
- Only add new alerts (not in current list)
- Only remove alerts not in new list
- Update alerts that changed (compare updated_at timestamp)

### 5.5 Map Bounds Filtering (Optional Enhancement)
- Filter alerts by current map viewport
- Only display alerts visible in current map bounds
- Update when map is panned/zoomed
- Reduces API load and improves performance

---

## 6. UI/UX Considerations

### 6.1 Alert Visibility
- Alerts should be visible but not overwhelming
- Use appropriate opacity for overlays (0.3-0.5 for circles/polygons)
- Icons should be clearly visible but not too large
- Consider z-index to ensure alerts appear above base map but below routes

### 6.2 Info Window Design
- Clean, readable design
- Include all relevant information
- Show timestamp in user-friendly format
- Consider adding "Dismiss" button for user's session
- Mobile-responsive design

### 6.3 Alert Legend (Optional)
- Add legend explaining alert types and colors
- Can be toggleable panel
- Helps users understand alert system

### 6.4 Filtering Controls (Optional Enhancement)
- Add UI controls to filter alerts by type/severity
- Checkboxes or dropdowns
- Update map display based on filters

---

## 7. Error Handling

### 7.1 API Errors
- Handle network errors gracefully
- Show user-friendly error messages
- Retry failed requests with exponential backoff
- Log errors for debugging

### 7.2 Data Validation
- Validate polygon_coordinates JSON format
- Handle malformed data gracefully
- Skip invalid alerts with console warning
- Don't break map if single alert is invalid

### 7.3 Edge Cases
- Handle alerts with missing coordinates
- Handle alerts with invalid radius
- Handle alerts with expired dates
- Handle timezone issues with dates
- Handle alerts created by deleted users

---

## 8. Performance Considerations

### 8.1 Database Queries
- Use `select_related('created_by')` for efficient queries
- Add database indexes on frequently filtered fields
- Use `only()` or `defer()` if only specific fields needed
- Consider pagination if large number of alerts

### 8.2 Frontend Performance
- Limit number of overlays displayed (if many alerts)
- Use clustering for point markers if many alerts in same area
- Debounce map bounds updates
- Clean up event listeners when alerts removed
- Use efficient marker rendering (marker clustering library if needed)

### 8.3 Caching (Optional Enhancement)
- Cache alerts API response (short TTL, e.g., 30 seconds)
- Use ETags or Last-Modified headers
- Consider Redis caching for frequently accessed alerts

---

## 9. Testing Considerations

### 9.1 Unit Tests
- Test SafetyAlert model methods
- Test `is_currently_active()` logic with various date scenarios
- Test `get_polygon_coordinates()` parsing
- Test validation methods

### 9.2 Integration Tests
- Test API endpoints
- Test alert creation via admin
- Test alert filtering
- Test alert expiration

### 9.3 Frontend Tests
- Test alert loading on map
- Test alert display (point, circle, polygon)
- Test info window opening
- Test dynamic updates
- Test error handling

### 9.4 Edge Case Tests
- Test with no alerts
- Test with many alerts (100+)
- Test with overlapping alerts
- Test with alerts outside map bounds
- Test with expired alerts
- Test with invalid data

---

## 10. Implementation Order

### Phase 1: Backend Foundation
1. Create SafetyAlert model
2. Create and run migration
3. Register model in admin
4. Test admin interface

### Phase 2: API Endpoints
1. Create `get_alerts_api` view
2. Add URL route
3. Test API with sample data
4. Add filtering support

### Phase 3: Frontend - Basic Display
1. Add JavaScript to load alerts
2. Implement point marker display
3. Implement info window
4. Test basic functionality

### Phase 4: Frontend - Advanced Display
1. Implement circle overlay display
2. Implement polygon overlay display
3. Add custom icons/colors
4. Test all alert types

### Phase 5: Dynamic Updates
1. Implement polling mechanism
2. Implement efficient update logic
3. Test dynamic updates
4. Optimize performance

### Phase 6: Polish & Testing
1. Add error handling
2. Add loading states
3. Test edge cases
4. Performance optimization
5. UI/UX improvements

---

## 11. Potential Issues & Solutions

### Issue 1: Too Many Alerts Cluttering Map
**Solution:** 
- Implement alert filtering UI
- Use marker clustering for point alerts
- Consider priority system (only show high/critical by default)
- Add toggle to show/hide alerts

### Issue 2: Performance with Many Alerts
**Solution:**
- Implement map bounds filtering
- Use efficient update mechanisms
- Consider pagination or limiting alerts per request
- Use marker clustering library

### Issue 3: Overlapping Alerts
**Solution:**
- Info windows should close when another opens
- Consider z-index layering based on severity
- Add visual indication of overlapping alerts

### Issue 4: Timezone Issues
**Solution:**
- Store dates in UTC
- Convert to user's timezone on frontend
- Use Django's timezone utilities

### Issue 5: Polygon Coordinate Format
**Solution:**
- Define clear JSON format: `[[lat, lng], [lat, lng], ...]`
- Add validation in model/form
- Provide example in admin help text
- Add helper function to validate format

### Issue 6: Alert Expiration
**Solution:**
- Use `is_currently_active()` method to check dates
- Consider cron job to auto-deactivate expired alerts
- Show expired alerts in admin with different styling

---

## 12. Future Enhancements (Out of Scope)

1. **Alert Categories/Subcategories** - More granular alert types
2. **Alert Severity Auto-Adjustment** - Auto-adjust based on time/conditions
3. **User Reports** - Allow users to report safety issues
4. **Alert History** - Track alert changes over time
5. **Push Notifications** - Notify users of critical alerts
6. **Alert Routing** - Auto-route around active alerts
7. **Multi-language Support** - Translate alerts
8. **Alert Images** - Attach photos to alerts
9. **Alert Analytics** - Track which alerts are viewed most
10. **Alert Scheduling** - Schedule alerts in advance

---

## 13. File Changes Summary

### Files to Create:
- `accounts/migrations/0005_safetyalert.py`

### Files to Modify:
- `accounts/models.py` - Add SafetyAlert model
- `accounts/admin.py` - Add SafetyAlertAdmin
- `accounts/views.py` - Add API endpoints
- `accounts/urls.py` - Add API routes
- `accounts/templates/accounts/map.html` - Add alert display JavaScript

### Files to Consider Creating:
- `accounts/static/icons/` - Custom alert icons (if using static files)
- `accounts/tests/test_alerts.py` - Test suite for alerts

---

## 14. Acceptance Criteria Verification

### ✅ Safety alerts shown as icons or colored zones on map
- Point alerts → Markers with custom icons
- Circle alerts → Colored circular overlays
- Polygon alerts → Colored polygon overlays

### ✅ Each alert includes short description and timestamp
- Description displayed in info window
- Timestamp shown in user-friendly format
- All alert details accessible via click

### ✅ Map updates dynamically when new alerts are added by admin
- Polling mechanism checks for updates every 30 seconds
- New alerts appear automatically
- Updated alerts reflect changes
- Expired alerts are removed

### ✅ Clicking an alert opens detail popup
- Info window opens on click
- Shows all alert information
- Only one info window open at a time
- Mobile-friendly design

---

## 15. Security Considerations

1. **Admin Only Creation** - Ensure only admins can create alerts (via admin interface)
2. **Input Validation** - Validate all user inputs (coordinates, dates, etc.)
3. **SQL Injection Prevention** - Use Django ORM (already safe)
4. **XSS Prevention** - Sanitize alert descriptions in templates
5. **Rate Limiting** - Consider rate limiting on API endpoint if needed
6. **CSRF Protection** - Not needed for GET endpoints, but ensure if POST endpoints added

---

This plan provides a comprehensive roadmap for implementing the safety alerts feature while minimizing bugs and ensuring a smooth user experience.

