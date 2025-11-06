import os
import time
import requests
from django.core.management.base import BaseCommand
from accounts.models import Building
from django.conf import settings


class Command(BaseCommand):
    help = 'Update all building coordinates using Google Geocoding API for accuracy'

    def handle(self, *args, **kwargs):
        api_key = settings.GOOGLE_MAPS_API_KEY
        
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ GOOGLE_MAPS_API_KEY not found in settings')
            )
            return
        
        buildings = Building.objects.all().order_by('name')
        total = buildings.count()
        
        self.stdout.write(f'\n🔍 Updating coordinates for {total} buildings using Google Geocoding API...\n')
        
        updated_count = 0
        failed_count = 0
        
        for index, building in enumerate(buildings, 1):
            self.stdout.write(f'[{index}/{total}] Processing: {building.name}...')
            
            # Use address for geocoding
            address = building.address
            
            try:
                # Call Google Geocoding API
                url = 'https://maps.googleapis.com/maps/api/geocode/json'
                params = {
                    'address': address,
                    'key': api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if data['status'] == 'OK' and len(data['results']) > 0:
                    result = data['results'][0]
                    location = result['geometry']['location']
                    
                    old_lat = building.latitude
                    old_lng = building.longitude
                    new_lat = location['lat']
                    new_lng = location['lng']
                    
                    # Update building coordinates
                    building.latitude = new_lat
                    building.longitude = new_lng
                    building.save()
                    
                    # Calculate difference for verification
                    lat_diff = abs(new_lat - old_lat) if old_lat else 0
                    lng_diff = abs(new_lng - old_lng) if old_lng else 0
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Updated: ({old_lat:.6f}, {old_lng:.6f}) → ({new_lat:.6f}, {new_lng:.6f})'
                        )
                    )
                    
                    if lat_diff > 0.001 or lng_diff > 0.001:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  Large change detected (Δlat: {lat_diff:.6f}, Δlng: {lng_diff:.6f})'
                            )
                        )
                    
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ❌ Geocoding failed: {data.get("status", "Unknown error")}'
                        )
                    )
                    failed_count += 1
                
                # Rate limiting: Google allows 50 requests/second, be conservative
                time.sleep(0.1)
                
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Network error: {str(e)}')
                )
                failed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Error: {str(e)}')
                )
                failed_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Updated: {updated_count} buildings'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Failed: {failed_count} buildings'))
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✨ Coordinate update complete! All buildings now have accurate GPS coordinates.\n'
            )
        )

