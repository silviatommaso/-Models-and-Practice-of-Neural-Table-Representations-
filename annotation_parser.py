import json
import re

from schema_reader import schema_reader


def extract_tables(sql, db_path):
    sql = sql.upper()
    tables = set()

    # takes all tables after FROM (including subqueries)
    from_matches = re.findall(r'FROM\s+([A-Z_]+)', sql)
    tables.update(from_matches)

    # takes all tables after JOIN
    join_matches = re.findall(r'JOIN\s+([A-Z_]+)', sql)
    tables.update(join_matches)


    # gets all schemas, primary keys and foreign keys for the tables in the query
    schema, table_serialized, primary_keys, foreign_keys = schema_reader(list(tables), db_path)

    return schema, table_serialized, primary_keys, foreign_keys


# funzione che estrae gli esempi di addestramento per un dato schema, filtrando quelli che contengono almeno una tabella in comune con lo schema del query
def extract_examples(schema, examples_path):

    if examples_path is None:
        return []

    with open(examples_path, 'r') as f:
        data = json.load(f)

    query_tables = set(schema.keys())

    matched_examples = []

    for example in data["examples"]:

        # nomi delle tabelle dell'esempio
        example_tables = {
            table["name"].upper()
            for table in example["tables"]
        }

        # almeno una tabella in comune
        if query_tables.intersection(example_tables):
            matched_examples.append(example)

    return matched_examples


def parse_annotations(file_path, db_path, examples_path):

    if file_path is None:
        raise ValueError("ANNOTATION_PATH environment variable not set")

    with open(file_path, 'r') as f:
        data = json.load(f)

    results = []

    for item in data['data']:

        nl = item['nl'].strip()
        sql = item['sql']

        schema, table_serialized, primary_keys, foreign_keys = extract_tables(sql, db_path)

        results.append({
            "nl": nl,
            "tables": list(schema.keys()),
            "schema": schema,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "table_serialized": table_serialized,
            "examples": extract_examples(schema, examples_path)
        })

    return results