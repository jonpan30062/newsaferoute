from django.core.management.base import BaseCommand
from accounts.models import Building


class Command(BaseCommand):
    help = 'Populate the database with real Georgia Tech buildings'

    def handle(self, *args, **kwargs):
        # Clear existing buildings
        Building.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing buildings'))

        # Real Georgia Tech buildings with actual addresses
        buildings_data = [
            {
                'name': '505 Tenth St',
                'code': '155',
                'address': '505 Tenth St. N.W., ATLANTA, GA',
                'latitude': 33.7756,
                'longitude': -84.3963,
                'description': 'Building Number: 155'
            },
            {
                'name': '575 Fourteenth Street Engineering Center',
                'code': '850',
                'address': '575 Fourteenth St. N.W., ATLANTA, GA',
                'latitude': 33.7789,
                'longitude': -84.3989,
                'description': 'Engineering Center - Building Number: 850'
            },
            {
                'name': '70 Fourth St',
                'code': '224',
                'address': '70 Fourth St. N.W., ATLANTA, GA',
                'latitude': 33.7752,
                'longitude': -84.3892,
                'description': 'Building Number: 224'
            },
            {
                'name': '760 Spring Street',
                'code': '173',
                'address': '760 Spring St. N.W., ATLANTA, GA',
                'latitude': 33.7778,
                'longitude': -84.3895,
                'description': 'Building Number: 173'
            },
            {
                'name': 'Aircraft Prototyping Laboratory',
                'code': '206',
                'address': '509 Tech Way N.W., ATLANTA, GA',
                'latitude': 33.7765,
                'longitude': -84.3955,
                'description': 'Aircraft prototyping and research - Building Number: 206'
            },
            {
                'name': 'Architecture (East)',
                'code': '076',
                'address': '245 Fourth St. N.W., ATLANTA, GA',
                'latitude': 33.7755,
                'longitude': -84.3880,
                'description': 'East Architecture Building - Building Number: 076'
            },
            {
                'name': 'Architecture (West)',
                'code': '075',
                'address': '247 Fourth St. N.W., ATLANTA, GA',
                'latitude': 33.7754,
                'longitude': -84.3882,
                'description': 'West Architecture Building - Building Number: 075'
            },
            {
                'name': 'Bill Moore Student Success Center',
                'code': '031',
                'address': '219 Uncle Heinie Way N.W., ATLANTA, GA',
                'latitude': 33.7745,
                'longitude': -84.3925,
                'description': 'Student Success Center - Building Number: 031'
            },
            {
                'name': 'Blake R. Van Leer',
                'code': '085',
                'address': '777 Atlantic Dr. N.W., ATLANTA, GA',
                'latitude': 33.7722,
                'longitude': -84.3958,
                'description': 'Van Leer Building - Building Number: 085'
            },
            {
                'name': 'Bunger-Henry',
                'code': '086',
                'address': '778 Atlantic Dr. N.W., ATLANTA, GA',
                'latitude': 33.7721,
                'longitude': -84.3957,
                'description': 'Bunger-Henry Building - Building Number: 086'
            },
            {
                'name': 'Centergy One',
                'code': '176',
                'address': '75 Fifth St. N.W., ATLANTA, GA',
                'latitude': 33.7780,
                'longitude': -84.3888,
                'description': 'Technology Square - Building Number: 176'
            },
            {
                'name': 'Cherry L. Emerson',
                'code': '066',
                'address': '310 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7778,
                'longitude': -84.3968,
                'description': 'Chemical Engineering Building - Building Number: 066'
            },
            {
                'name': 'Christopher W. Klaus Advanced Computing',
                'code': '153',
                'address': '266 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7770,
                'longitude': -84.3960,
                'description': 'Advanced Computing Building - Building Number: 153'
            },
            {
                'name': 'Civil Engineering (Old)',
                'code': '058',
                'address': '221 Bobby Dodd Way N.W., ATLANTA, GA',
                'latitude': 33.7738,
                'longitude': -84.3935,
                'description': 'Civil Engineering - Building Number: 058'
            },
            {
                'name': 'Clough Undergraduate Learning Commons',
                'code': '166',
                'address': '266 Fourth St. N.W., ATLANTA, GA',
                'latitude': 33.7747,
                'longitude': -84.3965,
                'description': 'Learning Commons and Library - Building Number: 166'
            },
            {
                'name': 'Colonel Frank F. Groseclose',
                'code': '056',
                'address': '765 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7765,
                'longitude': -84.4005,
                'description': 'Groseclose Building - Building Number: 056'
            },
            {
                'name': 'College of Computing',
                'code': '050',
                'address': '801 Atlantic Dr. N.W., ATLANTA, GA',
                'latitude': 33.7772,
                'longitude': -84.3965,
                'description': 'Computing - Building Number: 050'
            },
            {
                'name': 'Curran Street Parking Deck',
                'code': '139',
                'address': '875 Curran St. N.W., ATLANTA, GA',
                'latitude': 33.7795,
                'longitude': -84.4015,
                'description': 'Parking Deck - Building Number: 139'
            },
            {
                'name': "Daniel C. O'Keefe",
                'code': '033',
                'address': '151 Sixth St. N.W., ATLANTA, GA',
                'latitude': 33.7735,
                'longitude': -84.3910,
                'description': "O'Keefe Building - Building Number: 033"
            },
            {
                'name': 'Daniel F. Guggenheim',
                'code': '040',
                'address': '265 North Ave. N.W., ATLANTA, GA',
                'latitude': 33.7718,
                'longitude': -84.3955,
                'description': 'Aerospace Engineering - Building Number: 040'
            },
            {
                'name': 'David M. Smith',
                'code': '024',
                'address': '685 Cherry St. N.W., ATLANTA, GA',
                'latitude': 33.7745,
                'longitude': -84.3948,
                'description': 'Smith Building - Building Number: 024'
            },
            {
                'name': 'Domenico P. Savant',
                'code': '038',
                'address': '631 Cherry St. N.W., ATLANTA, GA',
                'latitude': 33.7742,
                'longitude': -84.3945,
                'description': 'Savant Building - Building Number: 038'
            },
            {
                'name': 'Dorothy M. Crosland Tower',
                'code': '100',
                'address': '260 Fourth Street N.W., ATLANTA, GA',
                'latitude': 33.7749,
                'longitude': -84.3967,
                'description': 'Library Tower - Building Number: 100'
            },
            {
                'name': 'Engineering Science and Mechanics',
                'code': '041',
                'address': '620 Cherry St. N.W., ATLANTA, GA',
                'latitude': 33.7740,
                'longitude': -84.3943,
                'description': 'ESM Building - Building Number: 041'
            },
            {
                'name': 'Exhibition Hall',
                'code': '217',
                'address': '460 Fourth St. N.W., ATLANTA, GA',
                'latitude': 33.7762,
                'longitude': -84.3995,
                'description': 'Exhibition Hall - Building Number: 217'
            },
            {
                'name': 'Ford Environmental Sciences and Technology',
                'code': '147',
                'address': '311 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7779,
                'longitude': -84.3969,
                'description': 'Environmental Sciences - Building Number: 147'
            },
            {
                'name': 'Fuller E. Callaway Jr. Manufacturing Research Center',
                'code': '126',
                'address': '813 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7768,
                'longitude': -84.4008,
                'description': 'Manufacturing Research - Building Number: 126'
            },
            {
                'name': 'Gilbert Hillhouse Boggs',
                'code': '103',
                'address': '770 State St. N.W., ATLANTA, GA',
                'latitude': 33.7725,
                'longitude': -84.3985,
                'description': 'Boggs Building - Building Number: 103'
            },
            {
                'name': 'Global Learning Center',
                'code': '170',
                'address': '84 Fifth St. N.W., ATLANTA, GA',
                'latitude': 33.7778,
                'longitude': -84.3890,
                'description': 'Global Learning Center - Building Number: 170'
            },
            {
                'name': 'Habersham',
                'code': '137',
                'address': '781 Marietta St. N.W., ATLANTA, GA',
                'latitude': 33.7795,
                'longitude': -84.4005,
                'description': 'Habersham Building - Building Number: 137'
            },
            {
                'name': 'Instructional Center',
                'code': '055',
                'address': '759 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7764,
                'longitude': -84.4002,
                'description': 'Instructional Center - Building Number: 055'
            },
            {
                'name': 'ISyE Main',
                'code': '057',
                'address': '755 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7763,
                'longitude': -84.4003,
                'description': 'Industrial & Systems Engineering - Building Number: 057'
            },
            {
                'name': 'J. Erskine Love Jr. Manufacturing',
                'code': '144',
                'address': '771 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7766,
                'longitude': -84.4006,
                'description': 'Love Manufacturing - Building Number: 144'
            },
            {
                'name': 'John Lewis Student Center',
                'code': '104',
                'address': '351 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7780,
                'longitude': -84.3975,
                'description': 'Student Center - Building Number: 104'
            },
            {
                'name': 'Joseph M. Pettit Microelectronics Research',
                'code': '095',
                'address': '791 Atlantic Dr. N.W., ATLANTA, GA',
                'latitude': 33.7771,
                'longitude': -84.3963,
                'description': 'Microelectronics Research - Building Number: 095'
            },
            {
                'name': 'Judge S. Price Gilbert Memorial Library',
                'code': '077',
                'address': '260 Fourth Street N.W., ATLANTA, GA',
                'latitude': 33.7748,
                'longitude': -84.3966,
                'description': 'Main Library - Building Number: 077'
            },
            {
                'name': 'Kendeda Building for Innovative Sustainable Design',
                'code': '210',
                'address': '422 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7785,
                'longitude': -84.3985,
                'description': 'Sustainable Design - Building Number: 210'
            },
            {
                'name': 'Molecular Science and Engineering',
                'code': '167',
                'address': '901 Atlantic Dr. N.W., ATLANTA, GA',
                'latitude': 33.7775,
                'longitude': -84.3970,
                'description': 'Molecular Science - Building Number: 167'
            },
            {
                'name': 'Paper Tricentennial',
                'code': '129',
                'address': '500 Tenth St. N.W., ATLANTA, GA',
                'latitude': 33.7758,
                'longitude': -84.3965,
                'description': 'Paper Tricentennial - Building Number: 129'
            },
            {
                'name': 'Paul Weber Space Science & Technology',
                'code': '098',
                'address': '275 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7772,
                'longitude': -84.3962,
                'description': 'Space Science Building - Building Number: 098'
            },
            {
                'name': 'Rich Computer Center',
                'code': '051',
                'address': '258 Fourth St. N.W., ATLANTA, GA',
                'latitude': 33.7750,
                'longitude': -84.3968,
                'description': 'Computer Center - Building Number: 051'
            },
            {
                'name': 'Roger A. and Helen B. Krone Engineered Biosystems',
                'code': '195',
                'address': '950 Atlantic Dr. N.W., ATLANTA, GA',
                'latitude': 33.7778,
                'longitude': -84.3975,
                'description': 'Biosystems Building - Building Number: 195'
            },
            {
                'name': 'Scheller College of Business',
                'code': '172',
                'address': '800 West Peachtree St. N.W., ATLANTA, GA',
                'latitude': 33.7775,
                'longitude': -84.3885,
                'description': 'Business School - Building Number: 172'
            },
            {
                'name': 'Skiles',
                'code': '002',
                'address': '686 Cherry St. N.W., ATLANTA, GA',
                'latitude': 33.7746,
                'longitude': -84.3949,
                'description': 'Skiles Classroom Building - Building Number: 002'
            },
            {
                'name': 'Stephen C. Hall',
                'code': '059',
                'address': '215 Bobby Dodd Way N.W., ATLANTA, GA',
                'latitude': 33.7737,
                'longitude': -84.3933,
                'description': 'Hall Building - Building Number: 059'
            },
            {
                'name': 'Technology Square Research',
                'code': '175',
                'address': '85 Fifth St. N.W., ATLANTA, GA',
                'latitude': 33.7779,
                'longitude': -84.3889,
                'description': 'Tech Square Research - Building Number: 175'
            },
            {
                'name': 'U.A. Whitaker',
                'code': '165',
                'address': '313 Ferst Dr. N.W., ATLANTA, GA',
                'latitude': 33.7779,
                'longitude': -84.3970,
                'description': 'Biomedical Engineering - Building Number: 165'
            },
            {
                'name': 'West Village Dining Commons',
                'code': '209',
                'address': '532 Eighth St. N.W., ATLANTA, GA',
                'latitude': 33.7788,
                'longitude': -84.4010,
                'description': 'West Village Dining - Building Number: 209'
            },
        ]

        created_count = 0

        for building_data in buildings_data:
            building = Building.objects.create(**building_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created: {building.name} ({building.code})')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {created_count} Georgia Tech buildings'
            )
        )

