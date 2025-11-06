"""
Management command to sync official Georgia Tech buildings with accurate geocoded coordinates.
Uses Google Geocoding API to ensure coordinates match building addresses precisely.
"""

import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import Building


class Command(BaseCommand):
    help = 'Sync official Georgia Tech buildings with accurate geocoded coordinates'

    def handle(self, *args, **kwargs):
        api_key = settings.GOOGLE_MAPS_API_KEY
        
        if not api_key:
            self.stdout.write(
                self.style.ERROR('❌ GOOGLE_MAPS_API_KEY not found in settings')
            )
            return
        
        # Official Georgia Tech buildings from campus directory
        official_buildings = [
            {'name': '505 Tenth St', 'code': '155', 'address': '505 Tenth St. N.W., Atlanta, GA 30332'},
            {'name': '575 Fourteenth Street Engineering Center', 'code': '850', 'address': '575 Fourteenth St. N.W., Atlanta, GA 30318'},
            {'name': '70 Fourth St', 'code': '224', 'address': '70 Fourth St. N.W., Atlanta, GA 30332'},
            {'name': '760 Spring Street', 'code': '173', 'address': '760 Spring St. N.W., Atlanta, GA 30332'},
            {'name': 'Aircraft Prototyping Laboratory', 'code': '206', 'address': '509 Tech Way N.W., Atlanta, GA 30332'},
            {'name': 'Architecture (East)', 'code': '076', 'address': '245 Fourth St. N.W., Atlanta, GA 30332'},
            {'name': 'Architecture (West)', 'code': '075', 'address': '247 Fourth St. N.W., Atlanta, GA 30332'},
            {'name': 'Bill Moore Student Success Center', 'code': '031', 'address': '219 Uncle Heinie Way N.W., Atlanta, GA 30332'},
            {'name': 'Blake R. Van Leer', 'code': '085', 'address': '777 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Bunger-Henry', 'code': '086', 'address': '778 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Centergy One', 'code': '176', 'address': '75 Fifth St. N.W., Atlanta, GA 30332'},
            {'name': 'Cherry L. Emerson', 'code': '066', 'address': '310 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Christopher W. Klaus Advanced Computing', 'code': '153', 'address': '266 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Civil Engineering (Old)', 'code': '058', 'address': '221 Bobby Dodd Way N.W., Atlanta, GA 30332'},
            {'name': 'Clough Undergraduate Learning Commons', 'code': '166', 'address': '266 Fourth St. N.W., Atlanta, GA 30332'},
            {'name': 'Colonel Frank F. Groseclose', 'code': '056', 'address': '765 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Computing (COC)', 'code': '050', 'address': '801 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Curran Street Parking Deck', 'code': '139', 'address': '875 Curran St. N.W., Atlanta, GA 30332'},
            {'name': "Daniel C. O'Keefe", 'code': '033', 'address': '151 Sixth St. N.W., Atlanta, GA 30332'},
            {'name': 'Daniel F. Guggenheim', 'code': '040', 'address': '265 North Ave. N.W., Atlanta, GA 30332'},
            {'name': 'David M. Smith', 'code': '024', 'address': '685 Cherry St. N.W., Atlanta, GA 30332'},
            {'name': 'Domenico P. Savant', 'code': '038', 'address': '631 Cherry St. N.W., Atlanta, GA 30332'},
            {'name': 'Dorothy M. Crosland Tower', 'code': '100', 'address': '260 Fourth Street N.W., Atlanta, GA 30332'},
            {'name': 'Emerson Addition', 'code': '066A', 'address': '310 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Engineering Science and Mechanics', 'code': '041', 'address': '620 Cherry St. N.W., Atlanta, GA 30332'},
            {'name': 'Exhibition Hall', 'code': '217', 'address': '460 Fourth St. N.W., Atlanta, GA 30332'},
            {'name': 'Ford Environmental Sciences and Technology', 'code': '147', 'address': '311 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Fuller E. Callaway Jr. Manufacturing Research Center', 'code': '126', 'address': '813 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'George Tower and Scheller Tower', 'code': '220', 'address': '65 Fifth Street N.W., Atlanta, GA 30332'},
            {'name': 'Gilbert Hillhouse Boggs', 'code': '103', 'address': '770 State St. N.W., Atlanta, GA 30332'},
            {'name': 'Global Learning Center', 'code': '170', 'address': '84 Fifth St. N.W., Atlanta, GA 30332'},
            {'name': 'GT Connector', 'code': '016A', 'address': '116 Bobby Dodd Way N.W., Atlanta, GA 30332'},
            {'name': 'Habersham', 'code': '137', 'address': '781 Marietta St. N.W., Atlanta, GA 30332'},
            {'name': 'Instructional Center', 'code': '055', 'address': '759 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'ISyE Main', 'code': '057', 'address': '755 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'J. Allen Couch', 'code': '115', 'address': '840 McMillan St. N.W., Atlanta, GA 30332'},
            {'name': 'J. Erskine Love Jr. Manufacturing', 'code': '144', 'address': '771 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'J.L. Daniel Laboratory', 'code': '022', 'address': '200 Bobby Dodd Way N.W., Atlanta, GA 30332'},
            {'name': 'Janie Austell Swann', 'code': '039', 'address': '613 Cherry St. N.W., Atlanta, GA 30332'},
            {'name': 'Jesse Mason', 'code': '111', 'address': '790 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'John Lewis Student Center', 'code': '104', 'address': '351 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'John Saylor Coon', 'code': '045', 'address': '654 Cherry St. N.W., Atlanta, GA 30332'},
            {'name': 'Joseph H. Howey', 'code': '081', 'address': '800 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Joseph M. Pettit Microelectronics Research', 'code': '095', 'address': '791 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Judge S. Price Gilbert Memorial Library', 'code': '077', 'address': '260 Fourth Street N.W., Atlanta, GA 30332'},
            {'name': 'Kendeda Building for Innovative Sustainable Design', 'code': '210', 'address': '422 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Lamar Allen Sustainable Education', 'code': '145', 'address': '788 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Manufacturing Related Disciplines Complex', 'code': '135', 'address': '801 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Marion L. Brittain "T" Room Addition', 'code': '072', 'address': '658 Williams St. N.W., Atlanta, GA 30332'},
            {'name': 'Molecular Science and Engineering', 'code': '167', 'address': '901 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Paper Tricentennial', 'code': '129', 'address': '500 Tenth St. N.W., Atlanta, GA 30332'},
            {'name': 'Paul Weber Space Science & Technology (SST3)', 'code': '098', 'address': '275 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Penny and Roe Stamps Student Center Commons', 'code': '214', 'address': '351 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Rich Computer Center', 'code': '051D', 'address': '258 Fourth St. N.W., Atlanta, GA 30332'},
            {'name': 'Roger A. and Helen B. Krone Engineered Biosystems', 'code': '195', 'address': '950 Atlantic Dr. N.W., Atlanta, GA 30332'},
            {'name': 'Scheller College of Business', 'code': '172', 'address': '800 West Peachtree St. N.W., Atlanta, GA 30332'},
            {'name': 'Skiles', 'code': '002', 'address': '686 Cherry St. N.W., Atlanta, GA 30332'},
            {'name': 'Stephen C. Hall', 'code': '059', 'address': '215 Bobby Dodd Way N.W., Atlanta, GA 30332'},
            {'name': 'Technology Square Research', 'code': '175', 'address': '85 Fifth St. N.W., Atlanta, GA 30332'},
            {'name': 'U.A. Whitaker', 'code': '165', 'address': '313 Ferst Dr. N.W., Atlanta, GA 30332'},
            {'name': 'West Village Dining Commons', 'code': '209', 'address': '532 Eighth St. N.W., Atlanta, GA 30332'},
        ]
        
        self.stdout.write(f'\n🔍 Syncing {len(official_buildings)} official Georgia Tech buildings...\n')
        
        updated_count = 0
        created_count = 0
        failed_count = 0
        
        for building_data in official_buildings:
            name = building_data['name']
            code = building_data['code']
            address = building_data['address']
            
            self.stdout.write(f'Processing: {name} ({code})...')
            
            try:
                # Geocode the address
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
                    lat = location['lat']
                    lng = location['lng']
                    
                    # Update or create building
                    building, created = Building.objects.update_or_create(
                        code=code,
                        defaults={
                            'name': name,
                            'address': address,
                            'latitude': lat,
                            'longitude': lng,
                            'description': f'Building Number: {code}'
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {name} at ({lat:.6f}, {lng:.6f})'))
                        created_count += 1
                    else:
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Updated: {name} at ({lat:.6f}, {lng:.6f})'))
                        updated_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f'  ❌ Geocoding failed: {data.get("status")}'))
                    failed_count += 1
                
                # Rate limiting
                time.sleep(0.15)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error: {str(e)}'))
                failed_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*60)
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {created_count} buildings'))
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated: {updated_count} buildings'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Failed: {failed_count} buildings'))
        self.stdout.write('='*60 + '\n')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ Sync complete! {created_count + updated_count} buildings now have accurate coordinates.\n'
            )
        )

