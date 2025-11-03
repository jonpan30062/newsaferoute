from django.core.management.base import BaseCommand
from accounts.models import Building


class Command(BaseCommand):
    help = 'Populate the database with sample campus buildings'

    def handle(self, *args, **kwargs):
        # Sample campus buildings (using generic university coordinates)
        buildings_data = [
            {
                'name': 'Student Union Building',
                'code': 'SUB',
                'address': '123 University Ave, Campus, CA 94000',
                'latitude': 37.871899,
                'longitude': -122.258537,
                'description': 'Main student center with dining and activities'
            },
            {
                'name': 'Engineering Building',
                'code': 'ENG',
                'address': '456 Tech Way, Campus, CA 94000',
                'latitude': 37.874730,
                'longitude': -122.257990,
                'description': 'Engineering classrooms and labs'
            },
            {
                'name': 'Science Hall',
                'code': 'SCI',
                'address': '789 Science Dr, Campus, CA 94000',
                'latitude': 37.873500,
                'longitude': -122.260000,
                'description': 'Biology, Chemistry, and Physics departments'
            },
            {
                'name': 'Library and Learning Center',
                'code': 'LIB',
                'address': '321 Knowledge Ln, Campus, CA 94000',
                'latitude': 37.872500,
                'longitude': -122.259500,
                'description': 'Main campus library with study spaces'
            },
            {
                'name': 'Business Administration Building',
                'code': 'BUS',
                'address': '654 Commerce St, Campus, CA 94000',
                'latitude': 37.870900,
                'longitude': -122.258000,
                'description': 'Business school and career services'
            },
            {
                'name': 'Recreation Center',
                'code': 'REC',
                'address': '987 Athletic Way, Campus, CA 94000',
                'latitude': 37.869500,
                'longitude': -122.260500,
                'description': 'Gym, pool, and fitness facilities'
            },
            {
                'name': 'Arts and Humanities Building',
                'code': 'ART',
                'address': '147 Creative Blvd, Campus, CA 94000',
                'latitude': 37.873000,
                'longitude': -122.256500,
                'description': 'Fine arts, music, and theater programs'
            },
            {
                'name': 'Medical Sciences Building',
                'code': 'MED',
                'address': '258 Health Plaza, Campus, CA 94000',
                'latitude': 37.875200,
                'longitude': -122.259800,
                'description': 'Pre-med and health sciences programs'
            },
            {
                'name': 'Computer Science Building',
                'code': 'CS',
                'address': '369 Innovation Dr, Campus, CA 94000',
                'latitude': 37.874100,
                'longitude': -122.256800,
                'description': 'Computer labs and technology center'
            },
            {
                'name': 'Residence Hall North',
                'code': 'RHN',
                'address': '741 Campus Dr, Campus, CA 94000',
                'latitude': 37.870000,
                'longitude': -122.262000,
                'description': 'Student housing and dormitories'
            }
        ]

        created_count = 0
        updated_count = 0

        for building_data in buildings_data:
            building, created = Building.objects.update_or_create(
                code=building_data['code'],
                defaults=building_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {building.name} ({building.code})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {building.name} ({building.code})')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {created_count} new buildings '
                f'and updated {updated_count} existing buildings'
            )
        )

