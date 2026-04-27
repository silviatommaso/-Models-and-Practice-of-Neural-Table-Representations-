import json
import re


def extract_tables(sql):
    sql = sql.upper()
    tables = set()

    # prende tutte le tabelle dopo FROM (anche subquery)
    from_matches = re.findall(r'FROM\s+([A-Z_]+)', sql)
    tables.update(from_matches)

    # prende tutte le tabelle dopo JOIN
    join_matches = re.findall(r'JOIN\s+([A-Z_]+)', sql)
    tables.update(join_matches)

    return list(tables)


def parse_annotations(file_path):

    if file_path is None:
        raise ValueError("ANNOTATION_PATH environment variable not set")

    with open(file_path, 'r') as f:
        data = json.load(f)

    results = []

    for item in data['data']:

        nl = item['nl'].strip()
        sql = item['sql']

        tables = extract_tables(sql)

        results.append({
            "nl": nl,
            "tables": tables
        })

    return results