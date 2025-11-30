from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Building
import requests
from bs4 import BeautifulSoup
import re
import time


class Command(BaseCommand):
    help = 'Fetch occupancy data from Waitz.io for Georgia Tech buildings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--building-code',
            type=str,
            help='Specific building code to update (optional)',
        )
        parser.add_argument(
            '--waitz-id',
            type=str,
            help='Waitz ID for the building (required if building-code not provided)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update all buildings with waitz_id set',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Fetch from main Waitz page for all buildings at once
            self.fetch_all_buildings_from_waitz()
        elif options['building_code']:
            # For single building, still fetch from main page
            self.fetch_all_buildings_from_waitz(specific_code=options['building_code'])
        else:
            self.stdout.write(self.style.ERROR('Please provide --building-code or --all'))

    def fetch_all_buildings_from_waitz(self, specific_code=None):
        """
        Fetch occupancy data for all buildings from the Waitz API.
        This is more efficient than individual requests per building.
        """
        try:
            url = 'https://waitz.io/live/gatech'
            self.stdout.write(f'Fetching data from Waitz API: {url}...')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to fetch Waitz API: HTTP {response.status_code}'))
                return
            
            # Parse JSON response
            try:
                data = response.json()
                waitz_buildings = data.get('data', [])
            except ValueError:
                self.stdout.write(self.style.ERROR('Failed to parse JSON response from Waitz'))
                return
            
            if not waitz_buildings:
                self.stdout.write(self.style.WARNING('No building data found in Waitz API response'))
                return
            
            self.stdout.write(f'Found {len(waitz_buildings)} buildings from Waitz API')
            
            # Match Waitz buildings to our database buildings
            updated_count = 0
            
            # Get buildings to update
            if specific_code:
                buildings = Building.objects.filter(code=specific_code)
            else:
                buildings = Building.objects.all()
            
            for building in buildings:
                # Try to match by name (case-insensitive, fuzzy matching)
                matched_data = self.match_building_api(building, waitz_buildings)
                
                if matched_data:
                    self.update_building_with_api_data(building, matched_data)
                    updated_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ Successfully updated {updated_count} buildings'))
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'✗ Error fetching Waitz API: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error processing Waitz data: {str(e)}'))
    
    def match_building_api(self, db_building, waitz_buildings):
        """
        Try to match a database building with Waitz API data.
        Uses fuzzy name matching.
        """
        # Try exact match first
        for waitz_bldg in waitz_buildings:
            waitz_name = waitz_bldg.get('name', '')
            if db_building.name.lower() == waitz_name.lower():
                return waitz_bldg
        
        # Try partial match
        for waitz_bldg in waitz_buildings:
            waitz_name = waitz_bldg.get('name', '')
            
            # Check if significant parts of the name match
            db_name_parts = set(db_building.name.lower().split())
            waitz_name_parts = set(waitz_name.lower().split())
            
            # Remove common words
            common_words = {'building', 'hall', 'center', 'tower', 'library', 'commons', 'the', 'and', 'of'}
            db_name_parts -= common_words
            waitz_name_parts -= common_words
            
            # If at least 2 significant words match, consider it a match
            matching_words = db_name_parts & waitz_name_parts
            if len(matching_words) >= 2:
                self.stdout.write(f'  Matched: {db_building.name} → {waitz_name}')
                return waitz_bldg
            
            # Check for abbreviations or partial matches
            if waitz_name.lower() in db_building.name.lower() or db_building.name.lower() in waitz_name.lower():
                self.stdout.write(f'  Matched: {db_building.name} → {waitz_name}')
                return waitz_bldg
        
        return None
    
    def update_building_with_api_data(self, building, waitz_data):
        """
        Update a building with occupancy data from Waitz API.
        """
        # Extract data from Waitz API response
        occupancy_percent = waitz_data.get('busyness') or waitz_data.get('percentage', 0) * 100
        occupancy_percent = int(occupancy_percent)
        
        # Determine status based on percentage
        if occupancy_percent < 30:
            status = 'not_busy'
        elif occupancy_percent < 60:
            status = 'moderate'
        elif occupancy_percent < 80:
            status = 'busy'
        else:
            status = 'very_busy'
        
        # Find best (least busy) study spot from sub-locations
        best_spot = self.find_best_study_spot(waitz_data.get('subLocs', []))
        
        # Extract operating hours
        operating_hours = waitz_data.get('hourSummary', '')
        if operating_hours.lower() == 'open':
            operating_hours = '24/7'
        elif operating_hours.lower() == 'closed':
            operating_hours = 'Closed'
        
        # Update building
        building.current_occupancy_percent = occupancy_percent
        building.occupancy_status = status
        building.occupancy_last_updated = timezone.now()
        
        # Update additional details if available
        if best_spot:
            building.best_study_spot = best_spot
        
        if operating_hours:
            building.operating_hours = operating_hours
        
        # Store Waitz ID for future reference
        if not building.waitz_id and waitz_data.get('id'):
            building.waitz_id = str(waitz_data.get('id'))
        
        building.save()
        
        spot_info = f', Best: {best_spot[:30]}...' if best_spot else ''
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Updated {building.name}: {occupancy_percent}% ({status}) - {waitz_data.get("people", "?")} people{spot_info}'
            )
        )
    
    def find_best_study_spot(self, sub_locs):
        """
        Find the least busy study spot from sub-locations.
        """
        if not sub_locs:
            return ''
        
        # Filter for available and open locations
        available_locs = [
            loc for loc in sub_locs
            if loc.get('isAvailable') and loc.get('isOpen')
        ]
        
        if not available_locs:
            return ''
        
        # Find the least busy location
        least_busy = min(available_locs, key=lambda x: x.get('busyness', 100))
        
        return least_busy.get('name', '')
    
    def parse_waitz_buildings(self, soup):
        """
        Parse building data from the Waitz page.
        Returns a dictionary of building data.
        """
        buildings = {}
        
        # Try different patterns to find building data
        # Pattern 1: Look for elements with building names and occupancy
        building_elements = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'building|location|card', re.I))
        
        for element in building_elements:
            try:
                # Extract building name
                name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'span'], class_=re.compile(r'name|title|location', re.I))
                if not name_elem:
                    name_elem = element.find(string=re.compile(r'[A-Z][a-z]+ [A-Z]|Building|Library|Center|Tower|Hall|Commons', re.I))
                
                if not name_elem:
                    continue
                
                building_name = name_elem.get_text().strip() if hasattr(name_elem, 'get_text') else str(name_elem).strip()
                
                # Extract occupancy percentage
                occupancy_text = element.find(string=re.compile(r'\d+%'))
                occupancy_percent = None
                
                if occupancy_text:
                    match = re.search(r'(\d+)%', occupancy_text)
                    if match:
                        occupancy_percent = int(match.group(1))
                
                # Extract status (Not Busy, Busy, etc.)
                status_text = element.get_text().lower()
                status = self.determine_status(status_text, occupancy_percent)
                
                if building_name and occupancy_percent is not None:
                    buildings[building_name] = {
                        'name': building_name,
                        'occupancy_percent': occupancy_percent,
                        'status': status,
                        'raw_html': str(element)[:500]  # Store snippet for debugging
                    }
                    
                    self.stdout.write(f'  Found: {building_name} - {occupancy_percent}% ({status})')
                    
            except Exception as e:
                continue
        
        return buildings
    
    def match_building(self, db_building, waitz_buildings):
        """
        Try to match a database building with Waitz data.
        Uses fuzzy name matching.
        """
        # Try exact match first
        for waitz_name, data in waitz_buildings.items():
            if db_building.name.lower() == waitz_name.lower():
                return data
        
        # Try partial match
        for waitz_name, data in waitz_buildings.items():
            # Check if significant parts of the name match
            db_name_parts = set(db_building.name.lower().split())
            waitz_name_parts = set(waitz_name.lower().split())
            
            # Remove common words
            common_words = {'building', 'hall', 'center', 'tower', 'library', 'commons', 'the', 'and', 'of'}
            db_name_parts -= common_words
            waitz_name_parts -= common_words
            
            # If at least 2 significant words match, consider it a match
            matching_words = db_name_parts & waitz_name_parts
            if len(matching_words) >= 2:
                self.stdout.write(f'  Matched: {db_building.name} → {waitz_name}')
                return data
            
            # Check for abbreviations (e.g., "CULC" for "Clough Undergraduate Learning Commons")
            if db_building.code.lower() in waitz_name.lower() or waitz_name.lower() in db_building.name.lower():
                self.stdout.write(f'  Matched: {db_building.name} → {waitz_name}')
                return data
        
        return None
    
    def determine_status(self, text, occupancy_percent):
        """
        Determine occupancy status from text and percentage.
        """
        if occupancy_percent is None:
            return ''
        
        # Try to extract from text first
        if 'not busy' in text or 'not crowded' in text:
            return 'not_busy'
        elif 'very busy' in text or 'extremely busy' in text or 'very crowded' in text:
            return 'very_busy'
        elif 'moderate' in text or 'somewhat busy' in text:
            return 'moderate'
        elif 'busy' in text or 'crowded' in text:
            return 'busy'
        
        # Fall back to percentage-based determination
        if occupancy_percent < 30:
            return 'not_busy'
        elif occupancy_percent < 60:
            return 'moderate'
        elif occupancy_percent < 80:
            return 'busy'
        else:
            return 'very_busy'
    
    def update_building_with_data(self, building, data):
        """
        Update a building with occupancy data.
        """
        building.current_occupancy_percent = data['occupancy_percent']
        building.occupancy_status = data['status']
        building.occupancy_last_updated = timezone.now()
        building.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Updated {building.name}: {data["occupancy_percent"]}% ({data["status"]})'
            )
        )
    
    def update_building_occupancy(self, building, waitz_id=None):
        """
        Fetch occupancy data from Waitz.io for a specific building.
        
        Note: This scrapes data from waitz.io. Please ensure compliance with
        their Terms of Service. Consider contacting Waitz for API access.
        """
        if waitz_id:
            building.waitz_id = waitz_id
            building.save()
        
        if not building.waitz_id:
            self.stdout.write(self.style.WARNING(f'No Waitz ID set for {building.name}. Skipping.'))
            return
        
        try:
            # Construct Waitz URL - format may vary, adjust as needed
            # Waitz uses slugs based on building names
            building_slug = building.name.lower().replace(' ', '-').replace("'", '').replace(',', '')
            url = f'https://waitz.io/gatech/{building_slug}'
            
            self.stdout.write(f'Fetching data for {building.name} from {url}...')
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse occupancy percentage
                occupancy_percent = self.extract_occupancy_percent(soup)
                
                # Parse occupancy status
                occupancy_status = self.extract_occupancy_status(soup)
                
                # Parse next hour prediction
                next_hour_prediction = self.extract_next_hour_prediction(soup)
                
                # Parse peak hours
                peak_hours = self.extract_peak_hours(soup)
                
                # Parse best study spot
                best_study_spot = self.extract_best_study_spot(soup)
                
                # Parse operating hours
                operating_hours = self.extract_operating_hours(soup)
                
                # Update building
                building.current_occupancy_percent = occupancy_percent
                building.occupancy_status = occupancy_status
                building.next_hour_prediction = next_hour_prediction
                building.peak_hours = peak_hours
                building.best_study_spot = best_study_spot
                building.operating_hours = operating_hours
                building.occupancy_last_updated = timezone.now()
                building.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Updated {building.name}: {occupancy_percent}% occupied ({occupancy_status})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'✗ Failed to fetch data for {building.name}: HTTP {response.status_code}')
                )
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error fetching data for {building.name}: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error processing data for {building.name}: {str(e)}')
            )

    def extract_occupancy_percent(self, soup):
        """Extract occupancy percentage from the page."""
        # Look for percentage in status text like "Not Busy (18%)"
        status_text = soup.find(string=re.compile(r'\d+%'))
        if status_text:
            match = re.search(r'(\d+)%', status_text)
            if match:
                return int(match.group(1))
        
        # Alternative: look for specific elements
        occupancy_elem = soup.find(class_=re.compile(r'occupancy|busy|percent', re.I))
        if occupancy_elem:
            match = re.search(r'(\d+)%', occupancy_elem.get_text())
            if match:
                return int(match.group(1))
        
        return None

    def extract_occupancy_status(self, soup):
        """Extract occupancy status (not_busy, moderate, busy, very_busy)."""
        status_text = soup.get_text().lower()
        
        if 'not busy' in status_text or 'not crowded' in status_text:
            return 'not_busy'
        elif 'moderate' in status_text or 'somewhat busy' in status_text:
            return 'moderate'
        elif 'very busy' in status_text or 'extremely busy' in status_text:
            return 'very_busy'
        elif 'busy' in status_text or 'crowded' in status_text:
            return 'busy'
        
        return ''

    def extract_next_hour_prediction(self, soup):
        """Extract next hour prediction text."""
        # Look for text containing "next hour"
        prediction_elem = soup.find(string=re.compile(r'next hour', re.I))
        if prediction_elem:
            parent = prediction_elem.find_parent()
            if parent:
                return parent.get_text().strip()
        
        return ''

    def extract_peak_hours(self, soup):
        """Extract peak hours information."""
        # Look for text containing "peak hours" or "peak"
        peak_elem = soup.find(string=re.compile(r'peak hours?', re.I))
        if peak_elem:
            parent = peak_elem.find_parent()
            if parent:
                text = parent.get_text()
                # Extract times like "3pm, 4pm, and 5pm"
                times_match = re.search(r'(\d+(?:am|pm)(?:\s*,\s*\d+(?:am|pm))*(?:\s+and\s+\d+(?:am|pm))?)', text, re.I)
                if times_match:
                    return times_match.group(1)
        
        return ''

    def extract_best_study_spot(self, soup):
        """Extract best study spot recommendation."""
        # Look for text containing "best" or "recommend"
        best_elem = soup.find(string=re.compile(r'best|recommend', re.I))
        if best_elem:
            parent = best_elem.find_parent()
            if parent:
                return parent.get_text().strip()[:255]  # Limit length
        
        return ''

    def extract_operating_hours(self, soup):
        """Extract operating hours information."""
        # Look for hours patterns like "9am-5pm" or "24/7"
        hours_elem = soup.find(string=re.compile(r'\d+(?:am|pm)?\s*-\s*\d+(?:am|pm)|24/7|open|closed', re.I))
        if hours_elem:
            parent = hours_elem.find_parent()
            if parent:
                return parent.get_text().strip()[:255]
        
        return ''

