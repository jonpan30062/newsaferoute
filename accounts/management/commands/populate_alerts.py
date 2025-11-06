from django.core.management.base import BaseCommand
from accounts.models import SafetyAlert, User, Building
from django.utils import timezone
from datetime import timedelta
import json


class Command(BaseCommand):
    help = 'Populate the database with sample safety alerts using Georgia Tech buildings'

    def handle(self, *args, **kwargs):
        # Get or create a test admin user for created_by
        admin_user, _ = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Get Georgia Tech buildings for addresses
        try:
            fourth_st_building = Building.objects.filter(name__icontains='Fourth St').first()
            ferst_building = Building.objects.filter(address__icontains='Ferst Dr').first()
            atlantic_building = Building.objects.filter(address__icontains='Atlantic Dr').first()
            cherry_st_building = Building.objects.filter(address__icontains='Cherry St').first()
            fifth_st_building = Building.objects.filter(address__icontains='Fifth St').first()
            
            self.stdout.write(f'Found buildings:')
            if fourth_st_building:
                self.stdout.write(f'  Fourth St: {fourth_st_building.name} - {fourth_st_building.address}')
            if ferst_building:
                self.stdout.write(f'  Ferst Dr: {ferst_building.name} - {ferst_building.address}')
            if atlantic_building:
                self.stdout.write(f'  Atlantic Dr: {atlantic_building.name} - {atlantic_building.address}')
            if cherry_st_building:
                self.stdout.write(f'  Cherry St: {cherry_st_building.name} - {cherry_st_building.address}')
            if fifth_st_building:
                self.stdout.write(f'  Fifth St: {fifth_st_building.name} - {fifth_st_building.address}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting buildings: {e}'))
            return

        # 250 feet in meters = 76.2 meters
        CIRCLE_RADIUS_METERS = 76.2
        
        # Sample safety alerts data using GT building addresses (no coordinates)
        alerts_data = [
            {
                'title': 'Construction Zone - Fourth Street',
                'description': 'Road construction and sidewalk repairs in progress on Fourth Street N.W. near the Clough Undergraduate Learning Commons. Please use alternate routes. Traffic reduced to one lane. Expected completion: 2 weeks.',
                'alert_type': 'construction',
                'severity': 'medium',
                'location_type': 'point',
                'address': fourth_st_building.address if fourth_st_building else 'Fourth Street N.W., ATLANTA, GA',
                'latitude': None,
                'longitude': None,
                'is_active': True,
                'start_date': timezone.now() - timedelta(days=2),
                'end_date': timezone.now() + timedelta(days=12),
            },
            {
                'title': 'Road Work - Ferst Drive',
                'description': 'Paving work in progress on Ferst Drive N.W. between the Engineering buildings. Traffic reduced to one lane. Expect delays. Use alternate routes if possible. Work expected to complete by end of week.',
                'alert_type': 'construction',
                'severity': 'high',
                'location_type': 'circle',
                'address': ferst_building.address if ferst_building else 'Ferst Drive N.W., ATLANTA, GA',
                'latitude': None,
                'longitude': None,
                'radius': CIRCLE_RADIUS_METERS,  # 0.2 miles radius
                'is_active': True,
                'start_date': timezone.now() - timedelta(hours=6),
                'end_date': timezone.now() + timedelta(days=5),
            },
            {
                'title': 'Emergency - Atlantic Drive Building',
                'description': 'Temporary closure due to emergency maintenance at building on Atlantic Drive N.W. Building evacuated. All classes relocated. Check with your professor for alternative locations. Building will reopen once safety inspection is complete.',
                'alert_type': 'emergency',
                'severity': 'critical',
                'location_type': 'point',
                'address': atlantic_building.address if atlantic_building else 'Atlantic Drive N.W., ATLANTA, GA',
                'latitude': None,
                'longitude': None,
                'is_active': True,
                'start_date': timezone.now() - timedelta(hours=1),
                'end_date': timezone.now() + timedelta(hours=4),
            },
            {
                'title': 'Maintenance Work - Cherry Street Area',
                'description': 'Parking lot and sidewalk maintenance in progress on Cherry Street N.W. Sections closed. Reduced parking available. Please use parking garages or street parking. Work expected to finish by end of week.',
                'alert_type': 'maintenance',
                'severity': 'low',
                'location_type': 'circle',
                'address': cherry_st_building.address if cherry_st_building else 'Cherry Street N.W., ATLANTA, GA',
                'latitude': None,
                'longitude': None,
                'radius': CIRCLE_RADIUS_METERS,  # 0.2 miles radius
                'is_active': True,
                'start_date': timezone.now() - timedelta(days=1),
                'end_date': timezone.now() + timedelta(days=6),
            },
            {
                'title': 'Wet Floor Hazard - Fifth Street Building',
                'description': 'Recent cleaning has left floors wet in the main corridor of building on Fifth Street N.W. Please proceed with caution and use alternative routes if possible. Floor should be dry within the hour.',
                'alert_type': 'hazard',
                'severity': 'medium',
                'location_type': 'point',
                'address': fifth_st_building.address if fifth_st_building else 'Fifth Street N.W., ATLANTA, GA',
                'latitude': None,
                'longitude': None,
                'is_active': True,
                'start_date': timezone.now() - timedelta(minutes=30),
                'end_date': timezone.now() + timedelta(hours=1),
            },
        ]

        created_count = 0
        updated_count = 0

        for alert_data in alerts_data:
            # Use title as unique identifier (in real scenario, you might want different logic)
            title = alert_data.pop('title')
            
            alert, created = SafetyAlert.objects.update_or_create(
                title=title,
                defaults={
                    **alert_data,
                    'created_by': admin_user
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {alert.title} ({alert.get_alert_type_display()}, {alert.get_severity_display()})'
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'↻ Updated: {alert.title} ({alert.get_alert_type_display()}, {alert.get_severity_display()})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {created_count} new alerts '
                f'and updated {updated_count} existing alerts'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'\nYou can now view these alerts on the map at /map/'
            )
        )
