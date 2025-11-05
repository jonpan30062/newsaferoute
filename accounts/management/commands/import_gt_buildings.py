from django.core.management.base import BaseCommand
from accounts.models import Building
import pandas as pd
import requests
import time
from django.conf import settings


class Command(BaseCommand):
    help = 'Import Georgia Tech buildings from Excel file using title and address columns'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='georgia_tech_buildings_with_dorms.xlsx',
            help='Path to Excel file'
        )
        parser.add_argument(
            '--geocode',
            action='store_true',
            help='Geocode addresses to get coordinates (requires Google Maps API key)'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        geocode = options['geocode']
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            self.stdout.write(f'Loaded {len(df)} rows from {file_path}')
            
            # Check required columns
            required_columns = ['Building Name', 'Address']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f'Missing required columns: {missing_columns}')
                )
                self.stdout.write(f'Available columns: {df.columns.tolist()}')
                return
            
            # Clear existing buildings
            Building.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing buildings'))
            
            # Get Google Maps API key if geocoding
            api_key = None
            if geocode:
                api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
                if not api_key:
                    self.stdout.write(
                        self.style.ERROR('Google Maps API key not found. Cannot geocode addresses.')
                    )
                    self.stdout.write('Set GOOGLE_MAPS_API_KEY in settings.py or use --no-geocode')
                    return
            
            created_count = 0
            skipped_count = 0
            
            for index, row in df.iterrows():
                building_name = str(row['Building Name']).strip()
                address = str(row['Address']).strip()
                
                # Skip rows with missing essential data
                if not building_name or building_name == 'nan' or not address or address == 'nan':
                    skipped_count += 1
                    continue
                
                # Get building number if available
                building_number = None
                if 'Building Number' in df.columns:
                    building_num = row['Building Number']
                    if pd.notna(building_num):
                        building_number = str(building_num).strip()
                
                # Combine address components
                full_address = address
                if 'City' in df.columns and pd.notna(row['City']):
                    full_address += f", {row['City']}"
                if 'State' in df.columns and pd.notna(row['State']):
                    full_address += f", {row['State']}"
                if 'Zip' in df.columns and pd.notna(row['Zip']):
                    full_address += f" {row['Zip']}"
                
                # Get coordinates
                latitude = None
                longitude = None
                
                # Try to use existing coordinates first
                if 'Latitude' in df.columns and 'Longitude' in df.columns:
                    lat = row['Latitude']
                    lng = row['Longitude']
                    if pd.notna(lat) and pd.notna(lng):
                        try:
                            latitude = float(lat)
                            longitude = float(lng)
                        except (ValueError, TypeError):
                            pass
                
                # Geocode if coordinates not available and geocoding is enabled
                if (latitude is None or longitude is None) and geocode and api_key:
                    self.stdout.write(f'  Geocoding: {building_name}...')
                    coordinates = self.geocode_address(full_address, api_key)
                    if coordinates:
                        latitude, longitude = coordinates
                        time.sleep(0.2)  # Rate limiting for API (200ms between requests)
                
                # Don't use default coordinates - we'll geocode addresses dynamically
                # Set coordinates to None so they'll be geocoded on-the-fly
                if latitude is None or longitude is None:
                    # Use a placeholder that will trigger geocoding in JavaScript
                    # We'll use the address to geocode dynamically
                    latitude = None
                    longitude = None
                    self.stdout.write(
                        self.style.WARNING(
                            f'No coordinates for {building_name} - will geocode from address on map'
                        )
                    )
                
                # If we still don't have coordinates, use address-based geocoding
                # For now, we'll store the address and geocode in JavaScript
                
                # Create building code from building number or use first letters of name
                if building_number:
                    code = str(building_number).zfill(3)  # Pad with zeros to 3 digits
                else:
                    # Generate code from building name
                    words = building_name.split()
                    code = ''.join([w[0].upper() for w in words[:3]])[:10]
                
                # Create description
                description = f"Building Number: {building_number}" if building_number else ""
                
                # Only create building if we have valid coordinates or address
                # If no coordinates, we'll use the address for geocoding
                if latitude is None or longitude is None:
                    # Use default GT campus coordinates as placeholder
                    # JavaScript will geocode the address dynamically
                    latitude = 33.7756
                    longitude = -84.3963
                
                # Create or update building
                building, created = Building.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': building_name,
                        'address': full_address,
                        'latitude': latitude,
                        'longitude': longitude,
                        'description': description
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created: {building.name} ({building.code})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'↻ Updated: {building.name} ({building.code})'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully imported {created_count} buildings'
                )
            )
            if skipped_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Skipped {skipped_count} rows with missing data')
                )
                
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing buildings: {str(e)}')
            )
            raise
    
    def geocode_address(self, address, api_key):
        """Geocode an address using Google Maps Geocoding API"""
        try:
            url = 'https://maps.googleapis.com/maps/api/geocode/json'
            
            # Ensure address includes Atlanta, GA for better results
            if 'Atlanta' not in address and 'ATLANTA' not in address:
                address = f"{address}, Atlanta, GA"
            
            params = {
                'address': address,
                'key': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Geocoded: {address[:50]}... → ({lat}, {lng})')
                )
                return lat, lng
            elif data['status'] == 'ZERO_RESULTS':
                self.stdout.write(
                    self.style.WARNING(f'  ✗ No results for: {address[:50]}...')
                )
                return None
            elif data['status'] == 'OVER_QUERY_LIMIT':
                self.stdout.write(
                    self.style.ERROR('  ✗ Geocoding API quota exceeded. Please wait or check your quota.')
                )
                return None
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ✗ Geocoding failed ({data["status"]}): {address[:50]}...')
                )
                return None
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'  ✗ Geocoding request error for {address[:50]}...: {str(e)}')
            )
            return None
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ✗ Geocoding error for {address[:50]}...: {str(e)}')
            )
            return None

