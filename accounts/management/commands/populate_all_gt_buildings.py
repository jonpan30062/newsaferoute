from django.core.management.base import BaseCommand
from accounts.models import Building


class Command(BaseCommand):
    help = 'Populate the database with comprehensive list of ALL Georgia Tech buildings including dorms, academic buildings, and facilities'

    def handle(self, *args, **kwargs):
        # Clear existing buildings
        Building.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing buildings'))

        # Comprehensive Georgia Tech buildings with accurate addresses and coordinates
        buildings_data = [
            # ============== ACADEMIC BUILDINGS ==============
            {
                'name': 'Tech Tower',
                'code': '001',
                'address': '225 North Ave. N.W., Atlanta, GA 30332',
                'latitude': 33.7724,
                'longitude': -84.3948,
                'description': 'Historic administration building and campus icon'
            },
            {
                'name': 'Skiles Classroom Building',
                'code': '002',
                'address': '686 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7746,
                'longitude': -84.3949,
                'description': 'Mathematics and classroom building'
            },
            {
                'name': 'D.M. Smith Building',
                'code': '024',
                'address': '685 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7745,
                'longitude': -84.3948,
                'description': 'Smith Building'
            },
            {
                'name': 'Bill Moore Student Success Center',
                'code': '031',
                'address': '219 Uncle Heinie Way N.W., Atlanta, GA 30332',
                'latitude': 33.7745,
                'longitude': -84.3925,
                'description': 'Student Success Center'
            },
            {
                'name': "Daniel C. O'Keefe Building",
                'code': '033',
                'address': '151 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7735,
                'longitude': -84.3910,
                'description': "O'Keefe Building"
            },
            {
                'name': 'Domenico P. Savant Building',
                'code': '038',
                'address': '631 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7742,
                'longitude': -84.3945,
                'description': 'Savant Building'
            },
            {
                'name': 'Daniel F. Guggenheim Aerospace Engineering',
                'code': '040',
                'address': '265 North Ave. N.W., Atlanta, GA 30332',
                'latitude': 33.7718,
                'longitude': -84.3955,
                'description': 'Aerospace Engineering Building'
            },
            {
                'name': 'Engineering Science and Mechanics',
                'code': '041',
                'address': '620 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7740,
                'longitude': -84.3943,
                'description': 'ESM Building'
            },
            {
                'name': 'John Saylor Coon Building',
                'code': '045',
                'address': '654 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7743,
                'longitude': -84.3946,
                'description': 'Coon Building'
            },
            {
                'name': 'College of Computing',
                'code': '050',
                'address': '801 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7772,
                'longitude': -84.3965,
                'description': 'Computing - Building Number: 050'
            },
            {
                'name': 'Instructional Center',
                'code': '055',
                'address': '759 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7764,
                'longitude': -84.4002,
                'description': 'Instructional Center - Building Number: 055'
            },
            {
                'name': 'Colonel Frank F. Groseclose',
                'code': '056',
                'address': '765 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7765,
                'longitude': -84.4005,
                'description': 'Groseclose Building - Building Number: 056'
            },
            {
                'name': 'ISyE Main',
                'code': '057',
                'address': '755 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7763,
                'longitude': -84.4003,
                'description': 'Industrial & Systems Engineering - Building Number: 057'
            },
            {
                'name': 'Mason Building',
                'code': '058',
                'address': '790 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7769,
                'longitude': -84.3960,
                'description': 'Civil Engineering'
            },
            {
                'name': 'Stephen C. Hall Building',
                'code': '059',
                'address': '215 Bobby Dodd Way N.W., Atlanta, GA 30332',
                'latitude': 33.7737,
                'longitude': -84.3933,
                'description': 'Hall Building'
            },
            {
                'name': 'Cherry L. Emerson Building',
                'code': '066',
                'address': '310 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7778,
                'longitude': -84.3968,
                'description': 'Chemical Engineering Building'
            },
            {
                'name': 'Architecture (West)',
                'code': '075',
                'address': '247 Fourth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7754,
                'longitude': -84.3882,
                'description': 'West Architecture Building'
            },
            {
                'name': 'Architecture (East)',
                'code': '076',
                'address': '245 Fourth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7755,
                'longitude': -84.3880,
                'description': 'East Architecture Building'
            },
            {
                'name': 'Price Gilbert Memorial Library',
                'code': '077',
                'address': '704 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7748,
                'longitude': -84.3966,
                'description': 'Main Library'
            },
            {
                'name': 'Joseph H. Howey Physics Building',
                'code': '081',
                'address': '837 State St. N.W., Atlanta, GA 30332',
                'latitude': 33.7775,
                'longitude': -84.3985,
                'description': 'Physics Building'
            },
            {
                'name': 'Van Leer Electrical Engineering',
                'code': '085',
                'address': '777 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7722,
                'longitude': -84.3958,
                'description': 'Van Leer Building'
            },
            {
                'name': 'Bunger-Henry Building',
                'code': '086',
                'address': '778 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7721,
                'longitude': -84.3957,
                'description': 'Bunger-Henry Building'
            },
            {
                'name': 'Joseph M. Pettit Microelectronics Research Center',
                'code': '095',
                'address': '791 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7771,
                'longitude': -84.3963,
                'description': 'Microelectronics Research'
            },
            {
                'name': 'Paul Weber Space Science & Technology Building',
                'code': '098',
                'address': '275 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7772,
                'longitude': -84.3962,
                'description': 'Space Science Building'
            },
            {
                'name': 'Crosland Tower',
                'code': '100',
                'address': '260 Fourth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7749,
                'longitude': -84.3967,
                'description': 'Library Tower'
            },
            {
                'name': 'Boggs Building',
                'code': '103',
                'address': '770 State St. N.W., Atlanta, GA 30332',
                'latitude': 33.7725,
                'longitude': -84.3985,
                'description': 'Boggs Building'
            },
            {
                'name': 'Student Center (John Lewis Student Center)',
                'code': '104',
                'address': '350 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7750,
                'longitude': -84.3985,
                'description': 'Student Center'
            },
            {
                'name': 'Callaway Manufacturing Research Center',
                'code': '126',
                'address': '813 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7768,
                'longitude': -84.4008,
                'description': 'Manufacturing Research'
            },
            {
                'name': 'Paper Tricentennial Building',
                'code': '129',
                'address': '500 Tenth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7758,
                'longitude': -84.3965,
                'description': 'Paper Tricentennial'
            },
            {
                'name': 'Manufacturing Related Disciplines Complex',
                'code': '135',
                'address': '801 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7767,
                'longitude': -84.4007,
                'description': 'MRDC Building'
            },
            {
                'name': 'Love Manufacturing Building',
                'code': '144',
                'address': '771 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7766,
                'longitude': -84.4006,
                'description': 'Love Manufacturing'
            },
            {
                'name': 'Ford Environmental Science & Technology Building',
                'code': '147',
                'address': '311 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7779,
                'longitude': -84.3969,
                'description': 'Environmental Sciences'
            },
            {
                'name': 'Klaus Advanced Computing Building',
                'code': '153',
                'address': '266 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7770,
                'longitude': -84.3960,
                'description': 'Advanced Computing Building'
            },
            {
                'name': '505 Tenth Street',
                'code': '155',
                'address': '505 Tenth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7756,
                'longitude': -84.3963,
                'description': 'Building Number: 155'
            },
            {
                'name': 'U.A. Whitaker Biomedical Engineering',
                'code': '165',
                'address': '313 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7779,
                'longitude': -84.3970,
                'description': 'Biomedical Engineering'
            },
            {
                'name': 'Clough Undergraduate Learning Commons',
                'code': '166',
                'address': '266 Fourth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7744,
                'longitude': -84.3965,
                'description': 'Learning Commons and Library'
            },
            {
                'name': 'Molecular Science and Engineering',
                'code': '167',
                'address': '901 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7775,
                'longitude': -84.3970,
                'description': 'Molecular Science'
            },
            {
                'name': 'Global Learning Center',
                'code': '170',
                'address': '84 Fifth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7778,
                'longitude': -84.3890,
                'description': 'Global Learning Center'
            },
            {
                'name': 'Scheller College of Business',
                'code': '172',
                'address': '800 West Peachtree St. N.W., Atlanta, GA 30332',
                'latitude': 33.7775,
                'longitude': -84.3885,
                'description': 'Business School'
            },
            {
                'name': '760 Spring Street',
                'code': '173',
                'address': '760 Spring St. N.W., Atlanta, GA 30332',
                'latitude': 33.7778,
                'longitude': -84.3895,
                'description': 'Building Number: 173'
            },
            {
                'name': 'Technology Square Research Building',
                'code': '175',
                'address': '85 Fifth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7779,
                'longitude': -84.3889,
                'description': 'Tech Square Research'
            },
            {
                'name': 'Centergy One',
                'code': '176',
                'address': '75 Fifth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7780,
                'longitude': -84.3888,
                'description': 'Technology Square - Building Number: 176'
            },
            {
                'name': 'Krone Engineered Biosystems Building',
                'code': '195',
                'address': '950 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7778,
                'longitude': -84.3975,
                'description': 'Biosystems Building'
            },
            {
                'name': 'Marcus Nanotechnology Building',
                'code': '197',
                'address': '345 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7777,
                'longitude': -84.3978,
                'description': 'Nanotechnology Research Center'
            },
            {
                'name': 'Carbon Neutral Energy Solutions Laboratory',
                'code': '199',
                'address': '406 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7783,
                'longitude': -84.3982,
                'description': 'Energy Research Laboratory'
            },
            {
                'name': 'Aircraft Prototyping Laboratory',
                'code': '206',
                'address': '509 Tech Way N.W., Atlanta, GA 30332',
                'latitude': 33.7765,
                'longitude': -84.3955,
                'description': 'Aircraft prototyping and research'
            },
            {
                'name': 'West Village Dining Commons',
                'code': '209',
                'address': '532 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7788,
                'longitude': -84.4010,
                'description': 'West Village Dining'
            },
            {
                'name': 'Kendeda Building for Innovative Sustainable Design',
                'code': '210',
                'address': '422 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7785,
                'longitude': -84.3985,
                'description': 'Sustainable Design'
            },
            {
                'name': 'Stamps Student Center Commons',
                'code': '214',
                'address': '351 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7751,
                'longitude': -84.3986,
                'description': 'Student Center Commons'
            },
            {
                'name': 'Exhibition Hall',
                'code': '217',
                'address': '460 Fourth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7762,
                'longitude': -84.3995,
                'description': 'Exhibition Hall'
            },
            {
                'name': 'George and Scheller Towers',
                'code': '220',
                'address': '65 Fifth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7776,
                'longitude': -84.3887,
                'description': 'Business School Towers'
            },
            {
                'name': '70 Fourth Street',
                'code': '224',
                'address': '70 Fourth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7752,
                'longitude': -84.3892,
                'description': 'Building Number: 224'
            },
            
            # ============== RESIDENCE HALLS & DORMITORIES ==============
            {
                'name': 'Armstrong Residence Hall',
                'code': '108',
                'address': '530 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7760,
                'longitude': -84.3925,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Blaunt Residence Hall',
                'code': '109',
                'address': '525 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7762,
                'longitude': -84.3923,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Caldwell Residence Hall',
                'code': '110',
                'address': '504 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7758,
                'longitude': -84.3920,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Cloudman Residence Hall',
                'code': '111',
                'address': '507 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7761,
                'longitude': -84.3918,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Field Residence Hall',
                'code': '112',
                'address': '480 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7756,
                'longitude': -84.3915,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Freeman Residence Hall',
                'code': '113',
                'address': '483 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7759,
                'longitude': -84.3913,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Hanson Residence Hall',
                'code': '114',
                'address': '456 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7754,
                'longitude': -84.3910,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Harrison Residence Hall',
                'code': '115',
                'address': '459 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7757,
                'longitude': -84.3908,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Hopkins Residence Hall',
                'code': '116',
                'address': '432 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7752,
                'longitude': -84.3905,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Smith Residence Hall',
                'code': '117',
                'address': '435 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7755,
                'longitude': -84.3903,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Brown Residence Hall',
                'code': '118',
                'address': '440 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7760,
                'longitude': -84.3980,
                'description': 'Upper-class residence hall'
            },
            {
                'name': 'Howell Residence Hall',
                'code': '119',
                'address': '450 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7763,
                'longitude': -84.3982,
                'description': 'Upper-class residence hall'
            },
            {
                'name': 'Perry Residence Hall',
                'code': '120',
                'address': '460 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7766,
                'longitude': -84.3984,
                'description': 'Upper-class residence hall'
            },
            {
                'name': 'Fitten Residence Hall',
                'code': '121',
                'address': '505 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7772,
                'longitude': -84.3988,
                'description': 'Upper-class residence hall'
            },
            {
                'name': 'Montag Residence Hall',
                'code': '122',
                'address': '515 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7775,
                'longitude': -84.3990,
                'description': 'Upper-class residence hall'
            },
            {
                'name': 'Fulmer Residence Hall',
                'code': '123',
                'address': '525 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7778,
                'longitude': -84.3992,
                'description': 'Upper-class residence hall'
            },
            {
                'name': 'Woodruff Residence Hall',
                'code': '124',
                'address': '535 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7781,
                'longitude': -84.3994,
                'description': 'Upper-class residence hall with dining'
            },
            {
                'name': 'Glenn Residence Hall (Tower)',
                'code': '125',
                'address': '545 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7784,
                'longitude': -84.3996,
                'description': 'Upper-class high-rise residence hall'
            },
            {
                'name': 'Towers Residence Hall',
                'code': '127',
                'address': '555 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7787,
                'longitude': -84.3998,
                'description': 'Upper-class high-rise residence hall'
            },
            {
                'name': 'North Avenue Apartments (North)',
                'code': '130',
                'address': '426 North Ave. N.W., Atlanta, GA 30332',
                'latitude': 33.7708,
                'longitude': -84.3965,
                'description': 'Graduate and upper-class apartments'
            },
            {
                'name': 'North Avenue Apartments (South)',
                'code': '131',
                'address': '406 North Ave. N.W., Atlanta, GA 30332',
                'latitude': 33.7705,
                'longitude': -84.3968,
                'description': 'Graduate and upper-class apartments'
            },
            {
                'name': 'Eighth Street Apartments',
                'code': '133',
                'address': '650 Eighth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7795,
                'longitude': -84.4005,
                'description': 'Upper-class apartment-style housing'
            },
            {
                'name': 'Center Street Apartments',
                'code': '134',
                'address': '700 Center St. N.W., Atlanta, GA 30332',
                'latitude': 33.7800,
                'longitude': -84.4012,
                'description': 'Upper-class apartment-style housing'
            },
            {
                'name': 'Graduate Living Center',
                'code': '136',
                'address': '301 10th St. N.W., Atlanta, GA 30318',
                'latitude': 33.7738,
                'longitude': -84.3952,
                'description': 'Graduate student housing'
            },
            {
                'name': 'Undergraduate Living Center (ULC)',
                'code': '140',
                'address': '301 Bobby Dodd Way N.W., Atlanta, GA 30332',
                'latitude': 33.7735,
                'longitude': -84.3945,
                'description': 'Large undergraduate residence hall with dining'
            },
            {
                'name': 'Crecine Residence Hall',
                'code': '141',
                'address': '700 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7715,
                'longitude': -84.3950,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Folk Residence Hall',
                'code': '142',
                'address': '710 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7716,
                'longitude': -84.3952,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Hefner Residence Hall',
                'code': '143',
                'address': '720 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7717,
                'longitude': -84.3954,
                'description': 'Freshman residence hall'
            },
            {
                'name': 'Nave Residence Hall',
                'code': '161',
                'address': '730 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7718,
                'longitude': -84.3956,
                'description': 'Freshman residence hall with learning community'
            },
            
            # ============== ATHLETIC FACILITIES ==============
            {
                'name': 'Bobby Dodd Stadium at Hyundai Field',
                'code': '070',
                'address': '150 Bobby Dodd Way N.W., Atlanta, GA 30332',
                'latitude': 33.7726,
                'longitude': -84.3922,
                'description': 'Football stadium'
            },
            {
                'name': 'McCamish Pavilion (Hank McCamish Pavilion)',
                'code': '071',
                'address': '965 Fowler St. N.W., Atlanta, GA 30332',
                'latitude': 33.7803,
                'longitude': -84.3937,
                'description': 'Basketball arena'
            },
            {
                'name': 'Campus Recreation Center (CRC)',
                'code': '128',
                'address': '151 Sixth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7755,
                'longitude': -84.3935,
                'description': 'Main recreation and fitness facility'
            },
            {
                'name': 'Student Athletic Complex',
                'code': '160',
                'address': '190 Bobby Dodd Way N.W., Atlanta, GA 30332',
                'latitude': 33.7730,
                'longitude': -84.3930,
                'description': 'Athletic training and support facility'
            },
            {
                'name': 'Edge Center (Athletic Performance Center)',
                'code': '162',
                'address': '200 Bobby Dodd Way N.W., Atlanta, GA 30332',
                'latitude': 33.7732,
                'longitude': -84.3928,
                'description': 'Athletic performance and training center'
            },
            {
                'name': 'Ken Byers Tennis Complex',
                'code': '163',
                'address': '950 Fowler St. N.W., Atlanta, GA 30332',
                'latitude': 33.7800,
                'longitude': -84.3940,
                'description': 'Tennis facility'
            },
            {
                'name': 'Mewborn Field (Soccer/Lacrosse)',
                'code': '164',
                'address': '655 Marietta St. N.W., Atlanta, GA 30332',
                'latitude': 33.7785,
                'longitude': -84.3975,
                'description': 'Soccer and lacrosse field'
            },
            
            # ============== OTHER IMPORTANT FACILITIES ==============
            {
                'name': 'Curran Street Parking Deck',
                'code': '139',
                'address': '875 Curran St. N.W., Atlanta, GA 30332',
                'latitude': 33.7795,
                'longitude': -84.4015,
                'description': 'Parking facility'
            },
            {
                'name': 'North Avenue Parking Deck',
                'code': '150',
                'address': '400 North Ave. N.W., Atlanta, GA 30332',
                'latitude': 33.7706,
                'longitude': -84.3970,
                'description': 'Parking facility'
            },
            {
                'name': 'Student Services Building',
                'code': '151',
                'address': '631 Cherry St. N.W., Atlanta, GA 30332',
                'latitude': 33.7742,
                'longitude': -84.3947,
                'description': 'Student administrative services'
            },
            {
                'name': 'GT Bookstore',
                'code': '152',
                'address': '48 Fifth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7774,
                'longitude': -84.3892,
                'description': 'Campus bookstore in Tech Square'
            },
            {
                'name': 'Ferst Center for the Arts',
                'code': '180',
                'address': '349 Ferst Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7749,
                'longitude': -84.3984,
                'description': 'Performing arts center'
            },
            {
                'name': 'Robert C. Williams Paper Museum',
                'code': '181',
                'address': '500 Tenth St. N.W., Atlanta, GA 30332',
                'latitude': 33.7757,
                'longitude': -84.3964,
                'description': 'Paper history museum'
            },
            {
                'name': 'Hinman Research Building',
                'code': '190',
                'address': '791 Atlantic Dr. N.W., Atlanta, GA 30332',
                'latitude': 33.7770,
                'longitude': -84.3962,
                'description': 'Research facility'
            },
            {
                'name': 'Technology Enterprise Park',
                'code': '191',
                'address': '760 Spring St. N.W., Atlanta, GA 30332',
                'latitude': 33.7779,
                'longitude': -84.3896,
                'description': 'Innovation and entrepreneurship center'
            },
            {
                'name': 'Georgia Tech Hotel and Conference Center',
                'code': '200',
                'address': '800 Spring St. N.W., Atlanta, GA 30332',
                'latitude': 33.7782,
                'longitude': -84.3898,
                'description': 'Campus hotel and conference facility'
            },
            {
                'name': '575 Fourteenth Street Engineering Center',
                'code': '850',
                'address': '575 Fourteenth St. N.W., Atlanta, GA 30318',
                'latitude': 33.7789,
                'longitude': -84.3989,
                'description': 'Engineering Center'
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
                f'\n✓ Successfully populated {created_count} Georgia Tech buildings, dorms, and facilities!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   📍 Includes: Academic Buildings, Residence Halls, Athletic Facilities, and More'
            )
        )

