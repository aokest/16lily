import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def reset_core_tables():
    with connection.cursor() as cursor:
        # 1. Get all tables starting with core_
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'core_%';
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("No core_ tables found.")
        else:
            print(f"Found {len(tables)} tables to drop: {tables}")
            
            # 2. Drop tables
            for table in tables:
                print(f"Dropping {table}...")
                cursor.execute(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;")
            
            print("All core_ tables dropped.")
            
        # 3. Clean django_migrations
        print("Cleaning django_migrations for app 'core'...")
        cursor.execute("DELETE FROM django_migrations WHERE app = 'core';")
        print(f"Deleted {cursor.rowcount} migration records.")

if __name__ == '__main__':
    try:
        reset_core_tables()
        print("Reset complete. Now run 'python manage.py migrate core'.")
    except Exception as e:
        print(f"Error: {e}")
