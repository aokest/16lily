import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Project, ProjectCard, Customer, User
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Import data from temp files'

    def handle(self, *args, **options):
        # In docker, BASE_DIR is /app/backend usually, or /app depending on settings.
        # Let's assume files are at /app/temp_projects.json
        # Wait, if I put them in 16lily/, they are at /app/temp_projects.json (if Dockerfile copies .)
        # Or mapped volume.
        
        # settings.BASE_DIR is usually /app/backend or similar.
        # Let's try to find them relative to manage.py which is at /app/manage.py
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        # core/management/commands/import... -> core/management/commands -> core/management -> core -> 16lily (root)
        
        # Actually, let's just use absolute path /app/temp_projects.json if we are in docker and root is mapped.
        # But to be safe, use relative to manage.py
        
        # manage.py is at 16lily/manage.py
        # This file is 16lily/core/management/commands/import_project_cards.py
        
        root_dir = "/app" # Standard for many docker setups
        if not os.path.exists(os.path.join(root_dir, 'manage.py')):
             root_dir = os.getcwd() # Fallback
             
        projects_file = os.path.join(root_dir, 'temp_projects.json')
        cards_file = os.path.join(root_dir, 'temp_cards.json')
        
        if not os.path.exists(projects_file):
            self.stdout.write(self.style.ERROR(f'File not found: {projects_file}'))
            return

        # Import Projects
        with open(projects_file, 'r', encoding='utf-8') as f:
            projects_data = json.load(f)
            
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            # Create if not exists
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.WARNING('Created admin user'))

        project_map = {} # code -> project_obj

        for p_data in projects_data:
            meta = p_data.get('meta', {})
            code = meta.get('projectNo')
            name = meta.get('name')
            cust_name = meta.get('customer')
            
            # Find/Create Customer
            customer = None
            if cust_name:
                customer, _ = Customer.objects.get_or_create(
                    name=cust_name,
                    defaults={'owner': admin_user}
                )
            
            # Find Manager
            manager = admin_user

            # Create Project
            project, created = Project.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'customer': customer,
                    'status': Project.Status.IN_PROGRESS if meta.get('status') == 'active' else Project.Status.PLANNING,
                    'description': meta.get('description', ''),
                    'budget': p_data.get('finance', {}).get('budgetIncome', 0),
                    'start_date': p_data.get('timeline', {}).get('start'),
                    'end_date': p_data.get('timeline', {}).get('end'),
                    'owner': manager
                }
            )
            project_map[code] = project
            self.stdout.write(self.style.SUCCESS(f'Imported Project: {name}'))

        # Import Cards
        if os.path.exists(cards_file):
            with open(cards_file, 'r', encoding='utf-8') as f:
                cards_data = json.load(f)
                
            for c_data in cards_data:
                card_id = c_data.get('cardId')
                # Try to match project code from cardId
                project = None
                for code, p in project_map.items():
                    if code in card_id:
                        project = p
                        break
                
                if not project:
                    # Fallback to first project if only one
                    if len(project_map) == 1:
                        project = list(project_map.values())[0]
                    else:
                        self.stdout.write(self.style.WARNING(f'Could not find project for card: {card_id}'))
                        continue

                # Map fields
                data_block = c_data.get('data', {})
                content = ""
                for k, v in data_block.items():
                    content += f"**{k}**: {v}\n\n"

                ProjectCard.objects.get_or_create(
                    title=c_data.get('title'),
                    project=project,
                    defaults={
                        'status': ProjectCard.Status.TODO if c_data.get('status') == 'active' else ProjectCard.Status.DONE,
                        'content': content,
                        'created_at': parse_datetime(c_data.get('updatedAt'))
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Imported Card: {c_data.get("title")}'))
