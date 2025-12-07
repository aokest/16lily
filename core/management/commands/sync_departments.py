from django.core.management.base import BaseCommand
from core.models import Department, DepartmentModel, UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Syncs old Enum-based departments to the new DepartmentModel hierarchy'

    def handle(self, *args, **options):
        self.stdout.write("Starting department synchronization...")

        # Map Enum to Name and Category
        # Category mapping based on Enum
        CATEGORY_MAP = {
            'SALES': DepartmentModel.Category.SALES,
            'GAME': DepartmentModel.Category.POC, # GAME -> POC/Tech Support or OTHER? Let's say POC for now based on description
            'GROUP_MARKETING': DepartmentModel.Category.FUNCTIONAL, # Marketing is functional/support usually, or OTHER
            'LAB': DepartmentModel.Category.LAB,
            'RND': DepartmentModel.Category.RND,
            'OTHER': DepartmentModel.Category.OTHER,
        }
        
        # Specific names
        NAME_MAP = {
            'SALES': '销售部',
            'GAME': '春秋GAME',
            'GROUP_MARKETING': '集团市场部',
            'LAB': '标准实践实验室',
            'RND': '研发中心',
            'OTHER': '其他部门',
        }

        with transaction.atomic():
            # 1. Ensure Root Departments exist
            dept_map = {} # Code -> Model Instance
            
            for code, label in Department.choices:
                name = NAME_MAP.get(code, label)
                category = CATEGORY_MAP.get(code, DepartmentModel.Category.OTHER)
                
                dept, created = DepartmentModel.objects.get_or_create(
                    name=name,
                    defaults={
                        'category': category,
                        'description': f'Automatically created from legacy department: {label}',
                        'order': 10
                    }
                )
                if created:
                    self.stdout.write(f"Created department: {name}")
                else:
                    # Update category if missing
                    if dept.category == DepartmentModel.Category.OTHER and category != DepartmentModel.Category.OTHER:
                         dept.category = category
                         dept.save()
                
                dept_map[code] = dept

            # 2. Sync User Profiles
            profiles = UserProfile.objects.all()
            updated_count = 0
            
            for profile in profiles:
                # If already linked, skip (or force update? Let's skip if linked to preserve manual changes)
                if profile.department_link:
                    continue
                
                if profile.department in dept_map:
                    profile.department_link = dept_map[profile.department]
                    profile.save()
                    updated_count += 1
                    self.stdout.write(f"Linked user {profile.user.username} to {profile.department_link.name}")

        self.stdout.write(self.style.SUCCESS(f"Synchronization complete. Updated {updated_count} user profiles."))
