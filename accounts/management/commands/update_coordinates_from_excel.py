from django.core.management.base import BaseCommand
from accounts.models import Building
import pandas as pd
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = 'Update building coordinates from georgia_tech_buildings_with_dorms.xlsx file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='georgia_tech_buildings_with_dorms.xlsx',
            help='Path to Excel file with coordinates'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def similarity(self, a, b):
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def find_best_match(self, excel_name, buildings):
        """Find the best matching building in database for an Excel row"""
        best_match = None
        best_score = 0.0
        
        for building in buildings:
            # Try exact match first
            if building.name.lower() == excel_name.lower():
                return building, 1.0
            
            # Calculate similarity
            score = self.similarity(building.name, excel_name)
            
            # Also check if building name contains key parts of excel name
            excel_words = set(excel_name.lower().split())
            building_words = set(building.name.lower().split())
            
            # Remove common words
            common_words = {'building', 'hall', 'center', 'tower', 'library', 'commons', 'the', 'and', 'of', 'st', 'street', 'dr', 'drive', 'nw', 'n.w.'}
            excel_words -= common_words
            building_words -= common_words
            
            # If significant words match, boost the score
            if len(excel_words) > 0 and len(building_words) > 0:
                word_overlap = len(excel_words & building_words) / max(len(excel_words), len(building_words))
                score = max(score, word_overlap * 0.8)
            
            if score > best_score:
                best_score = score
                best_match = building
        
        return best_match, best_score

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            self.stdout.write(f'Loaded {len(df)} rows from {file_path}')
            
            # Check required columns
            required_cols = ['Building Name', 'Latitude', 'Longitude']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                self.stdout.write(
                    self.style.ERROR(f'Missing required columns: {missing_cols}')
                )
                self.stdout.write(f'Available columns: {df.columns.tolist()}')
                return
            
            # Get all buildings from database
            buildings = list(Building.objects.all())
            self.stdout.write(f'Found {len(buildings)} buildings in database')
            
            if len(buildings) == 0:
                self.stdout.write(self.style.WARNING('No buildings in database to update'))
                return
            
            updated_count = 0
            not_found_count = 0
            skipped_count = 0
            already_updated = set()  # Track which buildings have been updated
            
            # Process each row in Excel
            for index, row in df.iterrows():
                excel_name = str(row['Building Name']).strip()
                latitude = row['Latitude']
                longitude = row['Longitude']
                
                # Skip if coordinates are missing
                if pd.isna(latitude) or pd.isna(longitude):
                    skipped_count += 1
                    continue
                
                # Find matching building
                building, score = self.find_best_match(excel_name, buildings)
                
                if building is None or score < 0.5:
                    # No good match found
                    not_found_count += 1
                    if not_found_count <= 5:  # Show first 5 not found
                        self.stdout.write(
                            self.style.WARNING(f'  ✗ No match found for: {excel_name}')
                        )
                    continue
                
                # Skip if this building was already updated (prefer exact matches)
                if building.id in already_updated:
                    # Only update again if this is an exact match and previous wasn't
                    if score < 1.0:
                        continue
                
                # Check if coordinates are different
                old_lat = float(building.latitude) if building.latitude else None
                old_lng = float(building.longitude) if building.longitude else None
                new_lat = float(latitude)
                new_lng = float(longitude)
                
                if old_lat == new_lat and old_lng == new_lng:
                    # Coordinates already match, skip
                    continue
                
                # Update coordinates
                if not dry_run:
                    building.latitude = new_lat
                    building.longitude = new_lng
                    building.save()
                
                already_updated.add(building.id)
                match_info = f"(match: {score:.2f})" if score < 1.0 else "(exact)"
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Updated {building.name}: ({old_lat}, {old_lng}) → ({new_lat}, {new_lng}) {match_info}'
                    )
                )
                updated_count += 1
            
            # Summary
            self.stdout.write('\n' + '='*60)
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully updated {updated_count} buildings')
            )
            if not_found_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {not_found_count} buildings from Excel not found in database')
                )
            if skipped_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {skipped_count} rows skipped (missing coordinates)')
                )
                
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating coordinates: {str(e)}')
            )
            raise

