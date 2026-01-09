import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import UserProfile, DepartmentModel, JobTitle

User = get_user_model()

def restore_profiles():
    users = User.objects.all()
    print(f"Checking {users.count()} users for profiles...")
    
    # Create a default department if needed
    dept, _ = DepartmentModel.objects.get_or_create(
        name='销售部',
        defaults={'category': 'SALES'}
    )
    
    # Create a default job title if needed
    job, _ = JobTitle.objects.get_or_create(
        name='销售经理',
        defaults={'category': 'SALES'}
    )

    count = 0
    for user in users:
        if not hasattr(user, 'profile'):
            print(f"Creating profile for {user.username}")
            # Check if UserProfile has 'name' field (it shouldn't based on models.py, but let's be safe)
            # Based on inspection, UserProfile has: user, phone, department(char), department_link(fk), 
            # report_to, job_category, job_rank, job_rank_level, job_title(fk), job_position, job_level
            
            UserProfile.objects.create(
                user=user,
                department_link=dept,
                department=dept.name, # Backward compatibility
                job_title=job,
                phone='13800138000'
            )
            count += 1
    
    print(f"Restored {count} profiles.")

if __name__ == '__main__':
    restore_profiles()
