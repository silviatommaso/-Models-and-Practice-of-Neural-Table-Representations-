import sqlite3



def schema_reader(table, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()

    conn.close()
    
    # Return only column names, excluding the first element which is the column index
    return columns



# function to get table's schema
def get_schema(tables, db_path):
    
    # Extract schema for each table
    schema = {}
    for table in tables:
        schema[table] = [column[1] for column in schema_reader(table, db_path)]
    return schema


# function to get primary keys of a table
def get_primary_keys(tables, db_path):

    primary_key = {}
    for table in tables:
        primary_key[table] = [column[1] for column in schema_reader(table, db_path) if column[5] == 1]

    return primary_key


#function to get foreign keys of a table
def get_foreign_keys(table, db_path):
    
    foreign_keys = schema_reader(table, db_path)

    result = []
    for fk in foreign_keys:
        result.append({
            "from": f"{table}.{fk[3]}",   
            "to": f"{fk[2]}.{fk[4]}"      
        })

    return result