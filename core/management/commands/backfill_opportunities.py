import json
from django.core.management.base import BaseCommand
from core.models import Project, Opportunity, Customer, User
from core.services.ai_service import AIService
from django.db import transaction
from django.utils import timezone

class Command(BaseCommand):
    help = 'Backfill opportunities for projects that do not have one'

    def handle(self, *args, **options):
        projects = Project.objects.filter(opportunity__isnull=True)
        count = projects.count()
        self.stdout.write(f"Found {count} projects without opportunities.")

        if count == 0:
            return

        ai_service = AIService()
        
        # Ensure we have a default user for ownership if project owner is missing
        default_user = User.objects.filter(is_superuser=True).first()
        if not default_user:
            default_user = User.objects.first()
            
        # Ensure we have a default customer
        default_customer, _ = Customer.objects.get_or_create(
            name="存量项目补充客户",
            defaults={'owner': default_user}
        )

        for project in projects:
            self.stdout.write(f"Processing project: {project.name} (ID: {project.id})")
            
            try:
                with transaction.atomic():
                    # 1. Try AI Analysis
                    ai_result = None
                    try:
                        prompt = f"""
                        Analyze the following project information and generate a suitable Opportunity Name and potential Customer Name.
                        The project is already established, so we need to backfill the opportunity data.
                        
                        Project Name: {project.name}
                        Description: {project.description or 'N/A'}
                        
                        Output JSON format:
                        {{
                            "opportunity_name": "string (e.g., 'xxx Project Opportunity')",
                            "customer_name": "string (Company name inferred from project)",
                            "probability": 100
                        }}
                        """
                        # Try to use AI service
                        # We use a broad try-except because AI service might not be fully configured or might fail
                        if hasattr(ai_service, '_call_llm_json'):
                             ai_result = ai_service._call_llm_json(prompt, project.description or project.name, intent='backfill_opportunity', entity='project')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"AI analysis failed for {project.name}, using defaults. Error: {e}"))
                    
                    # 2. Determine Values
                    opp_name = f"商机-{project.name}"
                    cust_name = default_customer.name
                    prob = 100 # Default for existing projects (usually won)
                    
                    if ai_result:
                        opp_name = ai_result.get('opportunity_name', opp_name)
                        cust_name = ai_result.get('customer_name', cust_name)
                        # Ensure probability is int
                        try:
                            prob = int(ai_result.get('probability', 100))
                        except:
                            prob = 100
                    
                    # 3. Create/Get Customer
                    # If AI suggested a customer name, try to find or create it
                    customer = default_customer
                    if cust_name and cust_name != "存量项目补充客户" and cust_name != "string":
                        customer, created = Customer.objects.get_or_create(
                            name=cust_name,
                            defaults={'owner': project.owner or default_user}
                        )
                        if created:
                            self.stdout.write(f"Created new customer: {cust_name}")

                    # 4. Create Opportunity
                    owner = project.owner or default_user
                    
                    opportunity = Opportunity.objects.create(
                        name=opp_name,
                        customer=customer,
                        user=owner,
                        status='WON', # Assume existing projects are WON. Note: Check model choices if 'WON' is valid string or integer
                        probability=prob,
                        description=f"Auto-generated for project {project.name}. Original description: {project.description}",
                        created_at=project.created_at if hasattr(project, 'created_at') else timezone.now()
                    )
                    
                    # 5. Link to Project
                    project.opportunity = opportunity
                    project.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Successfully linked project {project.name} to opportunity {opportunity.name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to process project {project.name}: {e}"))
