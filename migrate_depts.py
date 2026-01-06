from core.models import DepartmentModel

def migrate_departments():
    rules = [
        (['销售', '军团'], 'SALES'),
        (['市场', '人力', '财务'], 'FUNCTION'),
        (['交付', '实施'], 'POC'),
        (['研发', '产线', '中心'], 'RND'),
        (['实验室'], 'LAB'),
        (['管理'], 'MANAGEMENT'),
    ]
    
    updated_count = 0
    for dept in DepartmentModel.objects.all():
        old_cat = dept.category
        new_cat = None
        
        for keywords, cat in rules:
            if any(kw in dept.name for kw in keywords):
                new_cat = cat
                break
        
        if new_cat and new_cat != old_cat:
            dept.category = new_cat
            dept.save()
            print(f"Updated {dept.name}: {old_cat} -> {new_cat}")
            updated_count += 1
            
    print(f"Migration completed. Updated {updated_count} departments.")

if __name__ == "__main__":
    migrate_departments()
