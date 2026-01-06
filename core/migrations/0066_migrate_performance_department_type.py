from django.db import migrations, models
import django.db.models.deletion

def migrate_department_data(apps, schema_editor):
    PerformanceTarget = apps.get_model('core', 'PerformanceTarget')
    DepartmentModel = apps.get_model('core', 'DepartmentModel')
    
    # Mapping of old codes to new names
    mapping = {
        'SALES': '销售部',
        'GAME': '春秋GAME',
        'GROUP_MARKETING': '集团市场部',
        'LAB': '标准实践实验室',
        'RD': '研发中心',
        'OTHER': '其他部门'
    }
    
    # Get all departments for lookup
    depts = {d.name: d.id for d in DepartmentModel.objects.all()}
    
    for target in PerformanceTarget.objects.all():
        old_val = target.department_id # This is currently a string in the DB
        if not old_val:
            continue
            
        # Try to find the new ID
        new_name = mapping.get(old_val, old_val)
        new_id = depts.get(new_name)
        
        if new_id:
            # We use update() to avoid validation errors since the field type is still CharField in state
            PerformanceTarget.objects.filter(id=target.id).update(department_id=str(new_id))
        else:
            # If not found, set to null or a default
            PerformanceTarget.objects.filter(id=target.id).update(department_id=None)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_alter_performancetarget_department'),
    ]

    operations = [
        # 1. Migrate data: Convert string names to ID strings
        migrations.RunPython(migrate_department_data),
        
        # 2. Change column type from VARCHAR to INTEGER
        # We use raw SQL because AlterField might fail if the data isn't perfectly clean
        migrations.RunSQL(
            sql='ALTER TABLE core_performancetarget ALTER COLUMN department TYPE integer USING (CASE WHEN department=\'\' THEN NULL ELSE department::integer END);',
            reverse_sql='ALTER TABLE core_performancetarget ALTER COLUMN department TYPE varchar(255);',
        ),
    ]
