
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from core.models import (
    ApprovalRequest, ApprovalStatus,
    Opportunity, Competition, MarketActivity, SocialMediaAccount, SocialMediaStats
)

class Command(BaseCommand):
    help = 'Migrate legacy approval status to ApprovalRequest table'

    def handle(self, *args, **options):
        self.stdout.write("Starting approval migration...")
        
        # Get or create a fallback admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()
        
        counts = {'created': 0, 'skipped': 0}

        def migrate_model(model_class, status_field='status', creator_field='creator', approver_field=None):
            ct = ContentType.objects.get_for_model(model_class)
            # Filter for objects that have a relevant status
            objects = model_class.objects.filter(**{f"{status_field}__in": [
                ApprovalStatus.PENDING, 
                ApprovalStatus.APPROVED, 
                ApprovalStatus.REJECTED
            ]})
            
            for obj in objects:
                # Check existence
                if ApprovalRequest.objects.filter(content_type=ct, object_id=obj.id).exists():
                    counts['skipped'] += 1
                    continue
                
                # Determine applicant and approver
                applicant = getattr(obj, creator_field, admin_user) or admin_user
                approver = admin_user
                if approver_field and getattr(obj, approver_field, None):
                    approver = getattr(obj, approver_field)
                
                status_val = getattr(obj, status_field)
                
                ApprovalRequest.objects.create(
                    content_type=ct,
                    object_id=obj.id,
                    applicant=applicant,
                    approver=approver,
                    status=status_val,
                    reason="Legacy Data Migration",
                    created_at=obj.created_at if hasattr(obj, 'created_at') else None
                )
                counts['created'] += 1
                self.stdout.write(f"Migrated {model_class.__name__} {obj.id}: {status_val}")

        # 1. Opportunity (approval_status)
        migrate_model(Opportunity, status_field='approval_status', creator_field='creator', approver_field='sales_manager')
        
        # 2. Competition
        migrate_model(Competition, status_field='status', creator_field='creator', approver_field='confirmed_by')
        
        # 3. MarketActivity
        migrate_model(MarketActivity, status_field='status', creator_field='creator', approver_field='confirmed_by')
        
        # 4. SocialMediaAccount
        migrate_model(SocialMediaAccount, status_field='status', creator_field='creator')
        
        # 5. SocialMediaStats
        migrate_model(SocialMediaStats, status_field='status', creator_field='creator')

        self.stdout.write(self.style.SUCCESS(f"Migration complete. Created: {counts['created']}, Skipped: {counts['skipped']}"))
