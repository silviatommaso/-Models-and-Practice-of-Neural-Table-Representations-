import sqlite3


#format the results of a SQL query into a list of dictionaries 
def format_results(cursor, rows):
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]



# function to execute the SQL queries from the ground truth file and return the results in a structured format
def execute_ground_truth_queries(db_path, queries):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = []

    for q in queries:

        query_result = {
            "nl": q["nl"],
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
            "llama": None,
            "gpt": None
        }

        # ---------------- LLAMA ----------------
        sql = q["llama_sql"].strip()

        if sql.upper() == "NO QUERY;" or sql == "":
            query_result["llama"] = {"error": "no query generated"}
        else:
            query_result["llama"] = execute_queries(sql, cursor, query_result["llama"])

        # ---------------- GPT ----------------
        sql = q["gpt_sql"].strip()

        if sql.upper() == "NO QUERY;" or sql == "":
            query_result["gpt"] = {"error": "no query generated"}
        else:
            query_result["gpt"] = execute_queries(sql, cursor, query_result["gpt"])

        results.append(query_result)

    conn.close()

    return results




# Function to question the database with the SQL queries 
def execute_queries(sql, cursor, prediction):
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        prediction = format_results(cursor, rows)
    except Exception as e:
        prediction = {"error": str(e)}

    return prediction