from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Opportunity, Customer, Contact

class Command(BaseCommand):
    help = 'Sync existing Opportunity data to CRM models (Customer & Contact)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting CRM data sync...'))
        
        # Get default user for owner assignment (fallback to first superuser or specific user)
        default_owner = User.objects.filter(is_superuser=True).first()
        if not default_owner:
            self.stdout.write(self.style.ERROR('No superuser found to assign as default owner. Please create one first.'))
            return

        opportunities = Opportunity.objects.all()
        count_cust = 0
        count_contact = 0
        count_linked = 0

        for opp in opportunities:
            # 1. Sync Customer (Company)
            company_name = opp.customer_company
            if not company_name:
                continue
                
            customer, created = Customer.objects.get_or_create(
                name=company_name,
                defaults={
                    'owner': opp.sales_manager or default_owner,
                    'status': Customer.Status.ACTIVE,
                    'address': '（从商机同步，请完善）'
                }
            )
            
            if created:
                self.stdout.write(f"Created Customer: {company_name}")
                count_cust += 1
            
            # 2. Sync Contact (Person)
            contact_name = opp.customer_name
            if contact_name:
                # Check if contact exists for this customer
                contact, c_created = Contact.objects.get_or_create(
                    customer=customer,
                    name=contact_name,
                    defaults={
                        'department': opp.customer_org or '',
                        'notes': '（从商机同步，请完善）'
                    }
                )
                if c_created:
                    self.stdout.write(f"Created Contact: {contact_name} for {company_name}")
                    count_contact += 1

            # 3. Link Opportunity to Customer
            if not opp.customer:
                opp.customer = customer
                opp.save()
                count_linked += 1
        
        self.stdout.write(self.style.SUCCESS(f'Sync Complete: Created {count_cust} Customers, {count_contact} Contacts. Linked {count_linked} Opportunities.'))
