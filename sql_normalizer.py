import re
from dotenv import load_dotenv
import os
import json



load_dotenv()

ground_truth_path = os.getenv("ANNOTATION_PATH")


def normalize_sql(sql):

    if not sql:
        return ''

    # Remove code block markers (```sql ... ```)
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)

    # Remove extra whitespace
    sql = re.sub(r"\s+", " ", sql).strip()

    # Convert to uppercase
    sql = sql.upper()

    # ensures consistent spacing around operators (e.g., =, <, >)
    sql = re.sub(r"\s*=\s*", " = ", sql)

    # cut off anything after the first semicolon to avoid multiple statements
    idx = sql.find(";")
    if idx != -1:
        sql = sql[:idx + 1]

    # ensures exactly one semicolon at the end
    sql = re.sub(r";+\s*$", "", sql)
    sql = sql + ";"

    return sql



def normalize_ground_truth():

    #open ground truth file
    if ground_truth_path is None:
        raise ValueError("ANNOTATION_PATH environment variable not set")

    with open(ground_truth_path, 'r') as f:
        data = json.load(f)

    #normalization sql queries
    results = []

    for item in data['data']:

        id = item['id']
        nl = item['nl'].strip()
        sql = item['sql']

        # convert to uppercase for consistency
        sql = normalize_sql(sql)

        results.append({
            "id": id,
            "nl": nl,
            "sql": sql
        })

    return results