# scripts/init_db.py
from app.core.database import create_db_and_tables

create_db_and_tables()
print("DB initialized")
