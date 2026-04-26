import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

db_path = os.getenv("DB_PATH")

def schema_reader(table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()

    conn.close()
    
    # Return only column names, excluding the first element which is the column index
    return [column[1] for column in columns]


def get_schema(tables):
    
    # Extract schema for each table
    schema = {}
    for table in tables:
        schema[table] = schema_reader(table)
    
    return schema