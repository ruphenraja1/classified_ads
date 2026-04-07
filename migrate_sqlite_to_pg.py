import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

SQLITE_PATH = 'backend/db.sqlite3'

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'classifieds_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'AAlkas@*&^'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
}

BOOL_COLUMNS = {
    'auth_user': ['is_superuser', 'is_staff', 'is_active'],
    'ads_lov': ['is_active'],
}

def migrate():
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    pg_conn = psycopg2.connect(**DB_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    tables = [
        'django_migrations',
        'django_content_type',
        'auth_permission',
        'auth_group',
        'auth_user',
        'auth_group_permissions',
        'auth_user_groups',
        'auth_user_user_permissions',
        'django_session',
        'django_admin_log',
        'ads_lov',
        'ads_blockeduser',
        'ads_ad',
    ]
    
    for table in tables:
        print(f"Migrating {table}...")
        try:
            pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
            pg_conn.commit()
        except:
            pass
        
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  No rows to migrate")
            continue
        
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns_info = sqlite_cursor.fetchall()
        columns = [col[1] for col in columns_info]
        
        columns_str = ','.join([f'"{col}"' for col in columns])
        placeholders = ','.join(['%s'] * len(columns))
        
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        bool_cols = BOOL_COLUMNS.get(table, [])
        
        try:
            for row in rows:
                row_data = []
                for col in columns:
                    val = row[col]
                    if val is None:
                        row_data.append(None)
                    elif col in bool_cols:
                        row_data.append(bool(int(val)))
                    else:
                        row_data.append(val)
                pg_cursor.execute(query, tuple(row_data))
            pg_conn.commit()
            print(f"  Migrated {len(rows)} rows")
        except Exception as e:
            print(f"  Error: {e}")
            pg_conn.rollback()
    
    sqlite_conn.close()
    pg_conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
