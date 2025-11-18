# Light and Dark Mode Theme Implementation

## Overview
This document describes the implementation of light and dark mode themes for the SafeRoute campus map interface, completed as User Story 11.

## What Was Implemented

### 1. Theme System Architecture
A comprehensive theme system has been added that allows users to toggle between light and dark modes for improved visibility and comfort in varying lighting conditions.

### 2. Files Created

#### CSS Files
- **`accounts/static/accounts/css/theme.css`** - Main theme stylesheet with CSS variables
  - Contains all color definitions for light and dark modes
  - Defines theme variables for backgrounds, text, borders, buttons, alerts, and map components
  - Includes smooth transitions between themes
  - Provides theme-aware Bootstrap component styling

- **`accounts/static/accounts/css/map.css`** - Map-specific styles using theme variables
  - All map interface styles now use CSS variables
  - Supports dynamic theming for search results, info panels, toast notifications
  - Theme-aware safety alerts and saved routes panels

#### JavaScript Files
- **`accounts/static/accounts/js/theme.js`** - Theme management system
  - Handles theme initialization on page load
  - Manages theme toggling between light and dark modes
  - Persists user preference to localStorage
  - Respects system theme preference (prefers-color-scheme)
  - Watches for system theme changes
  - Updates toggle button icon dynamically

### 3. Files Modified

#### Templates
- **`accounts/templates/accounts/base.html`**
  - Added Bootstrap Icons CDN for theme toggle icon
  - Linked theme.css and theme.js files
  - Added theme toggle button to navbar (moon/sun icon)
  - Simplified inline styles to use theme variables

- **`accounts/templates/accounts/map.html`**
  - Replaced extensive inline CSS with map.css link
  - Converted remaining custom styles to use CSS variables
  - All map interface elements now support theming

## Theme Features

### Color Schemes

#### Light Mode (Default)
- Clean, bright interface with blue/green gradient
- Primary: Cyan/Sky Blue (#0ea5e9)
- Secondary: Emerald Green (#10b981)
- Accent: Amber/Gold (#fbbf24)
- White backgrounds with light gray accents

#### Dark Mode
- Dark slate backgrounds for reduced eye strain
- Adjusted colors for better visibility on dark backgrounds
- Primary: Brighter sky blue (#38bdf8)
- Secondary: Lighter emerald (#34d399)
- Dark backgrounds (#0f172a, #1e293b, #334155)
- Inverted Google Maps colors for consistency

### Theme Toggle Button
- Located in the navbar (far right)
- Moon icon in light mode → click to switch to dark
- Sun icon in dark mode → click to switch to light
- Smooth rotation animation on hover
- Accessible with proper ARIA labels

### Persistence & System Integration
- User preference saved to browser localStorage
- Persists across sessions and page reloads
- Automatically detects system theme preference on first visit
- Watches for system theme changes in real-time
- Works offline (no server-side storage required)

## Components with Theme Support

All UI components now support both light and dark modes:

✅ Navigation bar
✅ Cards and panels
✅ Forms and inputs
✅ Buttons (all variants)
✅ Alerts and notifications
✅ Tables
✅ Modals
✅ Dropdowns
✅ Toast notifications
✅ Map controls
✅ Search interface
✅ Building info windows
✅ Safety alerts
✅ Saved routes panel
✅ Favorites panel
✅ Loading overlays
✅ Google Maps (inverted colors in dark mode)

## How to Test

### Starting the Development Server
```bash
cd /Users/jpan/Downloads/saferoute
python manage.py runserver
```

### Testing Steps

1. **Navigate to any page** (e.g., http://localhost:8000)
2. **Locate the theme toggle button** in the navbar (moon/sun icon on the right)
3. **Click the toggle button** to switch between light and dark modes
4. **Verify the theme changes**:
   - Background colors should transition smoothly
   - Text remains readable in both modes
   - All UI components update their colors

5. **Test persistence**:
   - Refresh the page - theme should be remembered
   - Navigate to different pages - theme should persist
   - Close and reopen the browser - theme should be saved

6. **Test on different pages**:
   - Home page (/)
   - Map interface (/map/)
   - Dashboard (/dashboard/)
   - Login/Register pages
   - Settings page

7. **Test system theme integration** (optional):
   - Clear localStorage: Open browser console and run `localStorage.clear()`
   - Change your system's theme preference (OS settings)
   - Reload the page - it should match your system theme

8. **Test map interface specifically**:
   - Search for buildings
   - Calculate routes
   - View safety alerts
   - Check saved routes panel
   - Verify toast notifications
   - All should display correctly in both modes

## Browser Compatibility

The theme system is compatible with:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Technical Details

### CSS Variables
The theme uses CSS custom properties (variables) for dynamic theming:
```css
:root {
  --primary-color: #0ea5e9;
  --bg-primary: #ffffff;
  /* ... */
}

[data-theme="dark"] {
  --primary-color: #38bdf8;
  --bg-primary: #0f172a;
  /* ... */
}
```

### Theme Application
The theme is applied by setting a `data-theme="dark"` attribute on the `<html>` element:
```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

### LocalStorage Key
Theme preference is stored with key: `saferoute-theme`

## Future Enhancements (Optional)

Potential improvements for future iterations:
1. **Server-side storage**: Save theme preference to user profile in database
2. **Auto-scheduling**: Automatically switch themes based on time of day
3. **Custom themes**: Allow users to create custom color schemes
4. **Accessibility settings**: High contrast mode, font size adjustments
5. **Animation preferences**: Reduce motion for users with motion sensitivity

## Troubleshooting

### Theme not persisting?
- Check if localStorage is enabled in your browser
- Clear browser cache and try again
- Check browser console for JavaScript errors

### Styles not loading?
- Ensure Django development server is running
- Verify static files are being served (check browser network tab)
- Run `python manage.py collectstatic` if in production

### Toggle button not working?
- Check browser console for JavaScript errors
- Verify theme.js is loaded (check browser network tab)
- Ensure Bootstrap Icons CDN is loaded

## Files Summary

**New Files:**
- `accounts/static/accounts/css/theme.css` (8.9 KB)
- `accounts/static/accounts/css/map.css` (10.5 KB)
- `accounts/static/accounts/js/theme.js` (6.0 KB)

**Modified Files:**
- `accounts/templates/accounts/base.html`
- `accounts/templates/accounts/map.html`

**Total Implementation:**
- ~500 lines of CSS
- ~150 lines of JavaScript
- Theme system fully integrated across entire application

## Credits

Implemented for SafeRoute campus navigation application as part of User Story 11: Light and Dark Mode Themes.

Date: November 2024
