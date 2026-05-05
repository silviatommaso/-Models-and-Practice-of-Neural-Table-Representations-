import sqlite3



def schema_reader(tables, db_path):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    table_schema = {}
    table_serialized = {}
    primary_keys = {}
    foreign_keys = {}

    for table in tables:
        
        # Get all table names
        cursor.execute(f"PRAGMA table_info({table});")
        rows = cursor.fetchall()
        columns = [r[1] for r in rows]
        types = [r[2].lower() for r in rows]

        # Get data rows for serialization
        cursor.execute(f"SELECT * FROM {table};")
        data_rows = cursor.fetchall()

        table_schema[table] = columns
        table_serialized[table] = row_serialization(data_rows, columns, types)
        primary_keys[table] = get_primary_keys(rows)
        foreign_keys[table] = get_foreign_keys(table, cursor)

    conn.close()
    
    # Return only column names, excluding the first element which is the column index
    return table_schema, table_serialized, primary_keys, foreign_keys


# function to get primary keys of a table
def get_primary_keys(rows):
    primary_key = [r[1] for r in rows if r[5] == 1]
    return primary_key


# function to get foreign keys of a table
def get_foreign_keys(table, cursor):
    cursor.execute(f"PRAGMA foreign_key_list({table});")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "from": f"{table}.{row[3]}",   
            "to": f"{row[2]}.{row[4]}"      
        })

    return result

# function to serialize the table by row
def row_serialization(rows, columns, types):

    lines = []

    for row in rows:
        parts = []

        for col, typ, val in zip(columns, types, row):

            # normalizza tipo
            if "int" in typ:
                typ_str = "int"
            elif "char" in typ or "text" in typ:
                typ_str = "varchar"
            elif "real" in typ or "float" in typ or "double" in typ:
                typ_str = "float"
            else:
                typ_str = typ

            val_str = "NULL" if val is None else str(val)

            parts.append(f"{col}: {typ_str}: {val_str}")

        lines.append(" | ".join(parts))
    
    return " ... ".join(lines)