import re
import json


#-------------------------- UTILS FOR NORMALIZATION OF LLM RESPONSES -------------------------

def convert_type(value, typ):

    typ = typ.lower().replace(" ", "")
    value_str = str(value).strip()

    try:
        # -------- NUMBER(p,s) --------
        if "number" in typ:
            # se ha decimali → float
            if '.' in value_str:
                integer_part, decimal_part = value_str.split('.', 1)
                
                if set(decimal_part) == {'0'}:
                    return int(integer_part)
                
                return float(value_str)
            
            return int(value_str)

        # -------- INTEGER --------
        elif "int" in typ or "bigint" in typ:
            return int(value)

        # -------- BOOLEAN --------
        elif "bool" in typ:
            return value.lower() in ["true", "1", "yes"]

        # -------- STRING --------
        else:
            return value

    except:
        return value    


#----------------------------------------- MAIN FUNCTIONS ------------------------------------------------

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


def normalize_ground_truth(ground_truth_path):

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



def normalize_llm_output(text):

    if text is None:
        return []

    if not isinstance(text, str):
        text = str(text)

    if not text.strip():
        return []

    results = []


    # detect record separator
    records = text.strip().split("\n")


    # parse each record
    for record in records:

        item = {}

        # To handle cases where the LLM might not follow the expected format (for example when it adds not asked further explainations)
        if "|" not in record:
            continue

        parts = record.split("|")

        for part in parts:
            part = part.strip()

            if not part:
                continue

            tokens = [t.strip() for t in part.split(":")]

            if len(tokens) < 2:
                continue

            attribute = tokens[0]
            type = tokens[1]
            value = tokens[-1]

            item[attribute] = convert_type(value, type)

        if item:
            results.append(item)

    return results



def normalize(data_QA, data_TTSQL):

    normalized_QA = []
    normalized_TTSQL = []

    for item in data_QA:
        new_item = {
            "nl": item["nl"],
            "llama": normalize_llm_output(item.get("predictions", {}).get("llama-3.3-70b-versatile", [])),
            "gpt": normalize_llm_output(item.get("predictions", {}).get("gpt-oss-120b", []))
        }

        normalized_QA.append(new_item)



    for item in data_TTSQL:
        new_item = {
            "nl": item["nl"],
            "llama": normalize_sql(item["predictions"]["llama-3.3-70b-versatile"]),
            "gpt": normalize_sql(item["predictions"]["gpt-oss-120b"])
        }

        normalized_TTSQL.append(new_item)
        

    return normalized_QA, normalized_TTSQL