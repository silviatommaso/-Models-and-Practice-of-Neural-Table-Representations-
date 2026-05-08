import sqlite3

#------------------------------------------Utility functions-----------------------------------------

#format the results of a SQL query into a list of dictionaries 
def format_results(cursor, rows):

    columns = [desc[0] for desc in cursor.description]

    formatted_rows = []

    for row in rows:

        new_row = {}

        for col, val in zip(columns, row):

            # round floats
            if isinstance(val, float):
                val = round(val, 2)

                # se tipo 4.0 -> 4
                if val.is_integer():
                    val = int(val)

            new_row[col] = val

        formatted_rows.append(new_row)

    return formatted_rows


# Function to question the database with the SQL queries 
def execute_queries(sql, cursor, prediction):
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        prediction = format_results(cursor, rows)
    except Exception as e:
        prediction = {"error": str(e)}

    return prediction








# function to execute the SQL queries from the ground truth file and return the results in a structured format
def execute_ground_truth_queries(db_path, queries):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = []

    for q in queries:

        query_result = {
            "nl": q["nl"],
            "sql": q["sql"],
            "prediction": None
        }

        sql = q["sql"].strip()

        query_result["prediction"] = execute_queries(sql, cursor, query_result["prediction"])

        results.append(query_result)
        

    conn.close()

    return results



# function to execute LLM queries on the database and return the results in a structured format
def execute_llm_queries(db_path, queries):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = []

    for q in queries:

        query_result = {
            "nl": q["nl"],
            "sql_llama": q['llama'],
            "llama": None,
            "sql_gpt": q['gpt'],
            "gpt": None
        }

        # ---------------- LLAMA ----------------
        sql_llama = q["llama"].strip()

        if sql_llama.upper() == "NO QUERY;" or sql_llama == "":
            query_result["llama"] = {"error": "no query generated"}
        else:
            query_result["llama"] = execute_queries(sql_llama, cursor, query_result["llama"])

        # ---------------- GPT ----------------
        sql_gpt = q["gpt"].strip()

        if sql_gpt.upper() == "NO QUERY;" or sql_gpt == "":
            query_result["gpt"] = {"error": "no query generated"}
        else:
            query_result["gpt"] = execute_queries(sql_gpt, cursor, query_result["gpt"])

        results.append(query_result)

    conn.close()

    return results