# Testing Guide: Safety Concern Submission Feature

## Prerequisites
- ✅ Django server is running on http://127.0.0.1:8000/
- ✅ You have a user account (or can create one)

---

## Test 1: Access the Form

### Steps:
1. Open your browser and go to: **http://127.0.0.1:8000/**
2. If not logged in, click **"Login"** or **"Sign Up"** to create an account
3. After logging in, you should see the navigation menu

### Expected Results:
- ✅ Navigation menu shows **"Report Safety Concern"** link
- ✅ Dashboard shows **"Report Safety Concern"** button in Quick Actions
- ✅ Both links should work

### Test Navigation Links:
- Click **"Report Safety Concern"** in the navigation → Should go to `/report-safety-concern/`
- Click **"Report Safety Concern"** button on dashboard → Same result

---

## Test 2: Form Display

### Steps:
1. Navigate to the Report Safety Concern page
2. Observe the form layout

### Expected Results:
- ✅ Form displays with all required fields:
  - GPS checkbox ("Use Current Location (GPS)")
  - Location address textarea
  - Category dropdown
  - Description textarea
  - Photo upload field
- ✅ Form matches the app's theme (gradient background, card styling)
- ✅ All fields have proper labels and help text

---

## Test 3: GPS Location Feature

### Steps:
1. Check the **"Use Current Location (GPS)"** checkbox
2. Allow location access when browser prompts you
3. Wait for location to be captured

### Expected Results:
- ✅ Browser prompts for location permission
- ✅ GPS status message appears (green success message)
- ✅ Latitude and Longitude fields are auto-filled (hidden fields)
- ✅ Location address field is auto-populated with reverse-geocoded address (if Google Maps API is configured)
- ✅ If GPS fails, shows error message in red

### Test GPS Failure:
- Deny location permission → Should show error message
- Check/uncheck GPS checkbox → Location fields should clear when unchecked

---

## Test 4: Manual Location Entry

### Steps:
1. Leave GPS checkbox **unchecked**
2. Manually type in the Location address field: `"Near Engineering Building, Main Walkway"`

### Expected Results:
- ✅ You can type freely in the location field
- ✅ No GPS coordinates are set
- ✅ Form accepts manual entry

---

## Test 5: Form Validation

### Test 5a: Submit Empty Form
1. Leave all fields empty
2. Click **"Submit Safety Concern"**

### Expected Results:
- ✅ Form shows validation errors
- ✅ Location field: "Please provide a more specific location description"
- ✅ Description field: "Please provide a more detailed description"
- ✅ Category must be selected

### Test 5b: Submit with Minimal Valid Data
1. Fill in:
   - Location: `"Test Location"`
   - Category: `"Other"`
   - Description: `"This is a test"`
2. Click Submit

### Expected Results:
- ✅ Form validation passes (minimum 5 chars for location, 10 chars for description)
- ✅ Form submits successfully

---

## Test 6: Successful Submission (Without Photo)

### Steps:
1. Fill in the form:
   - **Location**: `"Near Student Union Building, Main Entrance"`
   - **Category**: Select `"Broken Light"`
   - **Description**: `"The light fixture near the main entrance is flickering and not providing adequate illumination. This poses a safety risk especially at night."`
   - **Photo**: Leave empty
2. Click **"Submit Safety Concern"**

### Expected Results:
- ✅ Form submits successfully
- ✅ **Green success message appears**: "Thank you! Your safety concern has been submitted successfully. Campus security will review it and take appropriate action."
- ✅ Form resets (or you stay on the page)
- ✅ Your submission appears in "Your Recent Submissions" section (if you submit multiple)

---

## Test 7: Photo Upload Feature

### Steps:
1. Fill in the form with valid data
2. Click **"Choose File"** or **"Browse"** for Photo
3. Select an image file (JPG, PNG, etc.)
4. Observe the preview

### Expected Results:
- ✅ Photo preview appears below the file input
- ✅ Preview shows the selected image
- ✅ File accepts common image formats

### Test Photo Validation:
1. Try uploading a file larger than 5MB → Should show error
2. Try uploading a non-image file (.txt, .pdf) → Should show error

---

## Test 8: Successful Submission (With Photo)

### Steps:
1. Fill in form with valid data
2. Upload a photo (optional)
3. Submit the form

### Expected Results:
- ✅ Submission succeeds with photo
- ✅ Success message appears
- ✅ Photo is saved (check in admin panel)

---

## Test 9: View in Admin Panel

### Steps:
1. Go to: **http://127.0.0.1:8000/admin/**
2. Log in with superuser credentials (or create one if needed)
3. Navigate to **"Safety Concerns"** under Accounts section

### Expected Results:
- ✅ List view shows all submitted concerns with:
  - Category
  - Location (shortened)
  - User who submitted
  - Status badge (colored)
  - Created date
  - Photo indicator (✓ Yes / ✗ No)
- ✅ You can filter by Category, Status, Created date
- ✅ You can search by location, description, or user

### Test Admin Actions:
1. Click on a concern to view details
2. Check fields:
   - Concern Information (category, description, location, coordinates)
   - Photo preview (if uploaded)
   - Status & Tracking
   - Admin Notes section
3. Try changing status dropdown
4. Add admin notes
5. Save changes

### Test Bulk Actions:
1. Select multiple concerns using checkboxes
2. Use Actions dropdown:
   - Mark as pending
   - Mark as in review
   - Mark as resolved
   - Mark as dismissed
3. Click **"Go"**

### Expected Results:
- ✅ Status changes apply to selected items
- ✅ Success message shows count of updated items
- ✅ List view updates with new status badges

---

## Test 10: Recent Submissions Display

### Steps:
1. Submit 2-3 different safety concerns
2. Return to the Report Safety Concern page
3. Scroll down to "Your Recent Submissions" section

### Expected Results:
- ✅ Shows your last 5 submissions
- ✅ Each shows:
  - Category name
  - Location (truncated)
  - Submission date/time
  - Status badge with color
- ✅ Submissions are ordered by most recent first

---

## Test 11: User Experience Flow

### Complete User Journey:
1. **Login** → Dashboard
2. Click **"Report Safety Concern"** from navigation
3. Fill form with GPS location
4. Select category: **"Unsafe Path"**
5. Add description: **"The walkway between Engineering and Science buildings has a large pothole that could cause someone to trip. It's been there for weeks."**
6. Upload a photo (optional)
7. Submit
8. See confirmation message
9. Check admin panel to verify it's stored

### Expected Results:
- ✅ Smooth flow from navigation → form → submission → confirmation
- ✅ All data is saved correctly
- ✅ User feels confident their concern was submitted

---

## Test 12: Edge Cases

### Test 12a: Very Long Location
- Enter location with 500+ characters
- Should accept and store

### Test 12b: Very Long Description
- Enter description with 1000+ characters
- Should accept and store

### Test 12c: Special Characters
- Use special characters in location/description: `"Location: Near Café & Restaurant #1!"`
- Should handle correctly

### Test 12d: Multiple Submissions
- Submit 10+ concerns
- Verify only 5 most recent show in "Recent Submissions"

---

## Test 13: Responsive Design

### Steps:
1. Open the form on different screen sizes:
   - Desktop (1920x1080)
   - Tablet (768px width)
   - Mobile (375px width)
2. Resize browser window

### Expected Results:
- ✅ Form is responsive and readable on all sizes
- ✅ Navigation menu works on mobile (hamburger menu)
- ✅ Photo preview scales appropriately
- ✅ All buttons are accessible

---

## Test 14: Error Handling

### Test 14a: Network Issues
- Submit form while offline → Should show appropriate error

### Test 14b: Invalid Image Format
- Try uploading .exe, .zip, .docx → Should reject with error message

### Test 14c: Large File Upload
- Try uploading 10MB image → Should reject with error message

---

## Verification Checklist

After testing, verify:

- [ ] Form is accessible from navigation menu
- [ ] Form is accessible from dashboard
- [ ] GPS location works (with permission)
- [ ] Manual location entry works
- [ ] Form validation works (required fields)
- [ ] Photo upload works
- [ ] Photo preview displays
- [ ] Successful submission shows confirmation message
- [ ] Submissions appear in admin panel
- [ ] Admin can view all details
- [ ] Admin can change status
- [ ] Admin can add notes
- [ ] Recent submissions display works
- [ ] Form matches app theme/styling
- [ ] Responsive design works
- [ ] Error messages are clear

---

## Creating a Test Superuser (If Needed)

If you don't have admin access:

```bash
cd /Users/sidjkadam/Documents/saferoute
python3 manage.py createsuperuser
```

Follow prompts to create admin account.

---

## Quick Test Commands

Check if server is running:
```bash
curl http://127.0.0.1:8000/
```

Check form URL (should redirect to login if not authenticated):
```bash
curl -I http://127.0.0.1:8000/report-safety-concern/
```

---

## Notes

- The form requires authentication (login required)
- GPS location requires browser permission
- Photo uploads are stored in `media/safety_concerns/` directory
- All submissions start with status "Pending Review"
- Admin can change status and add notes for internal tracking

---

## Troubleshooting

**Issue**: Form doesn't load
- Check server is running: `python3 manage.py runserver`
- Check URL: http://127.0.0.1:8000/report-safety-concern/

**Issue**: GPS doesn't work
- Check browser permissions (Chrome: Settings → Privacy → Location)
- Try HTTPS (some browsers require HTTPS for geolocation)
- Check browser console for errors

**Issue**: Photo doesn't upload
- Check file size (< 5MB)
- Check file format (JPG, PNG, GIF, WebP)
- Check `media/` directory exists and is writable

**Issue**: Can't access admin
- Create superuser: `python3 manage.py createsuperuser`
- Check admin URL: http://127.0.0.1:8000/admin/

