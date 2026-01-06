
import os
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from core.models import Project
from django.contrib.auth.models import User
from core.views import ProjectViewSet
from core.serializers import ProjectSerializer
from rest_framework.test import APIRequestFactory

def test_sync():
    # 1. Create a dummy project
    admin = User.objects.get(username='admin')
    p = Project.objects.create(name="Test Sync Project", owner=admin, code="TEST-001")
    print(f"Initial Owner: {p.owner.username}")

    # 2. Prepare data with new sales manager "kuangtu" (assuming kuangtu exists)
    # kuangtu is '狂徒'
    kuangtu = User.objects.get(username='kuangtu')
    print(f"Target Owner: {kuangtu.username} ({kuangtu.last_name}{kuangtu.first_name})")

    # 3. Simulate Update
    view = ProjectViewSet()
    view.request = APIRequestFactory().put('/projects/')
    view.request.user = admin
    
    # Payload
    data = {
        'name': 'Test Sync Project Updated',
        'extra_data': {
            'sales_managers': ['狂徒'], # Should match kuangtu
            'delivery_managers': [],
            'product_managers': []
        }
    }
    
    # Serializer
    serializer = ProjectSerializer(instance=p, data=data, partial=True)
    if serializer.is_valid():
        print("Serializer Valid.")
        # Call perform_update manually
        view.perform_update(serializer)
        
        # 4. Check Result
        p.refresh_from_db()
        print(f"Updated Owner: {p.owner.username}")
        if p.owner.username == 'kuangtu':
            print("SUCCESS: Owner synced.")
        else:
            print("FAILURE: Owner NOT synced.")
    else:
        print("Serializer Invalid:", serializer.errors)

if __name__ == "__main__":
    try:
        test_sync()
    except Exception as e:
        print(f"Error: {e}")
