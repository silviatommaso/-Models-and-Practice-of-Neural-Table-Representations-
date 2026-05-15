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


# function to extract training examples
def extract_examples(schema, examples_path):

    if examples_path is None:
        return []

    with open(examples_path, 'r') as f:
        data = json.load(f)

    query_tables = set(schema.keys())

    matched_examples = []

    for example in data["examples"]:

        # table names in the example
        example_tables = {
            table["name"].upper()
            for table in example["tables"]
        }

        # at least a table in common
        if query_tables.intersection(example_tables):
            matched_examples.append(example)

    return matched_examples


# function to extract attribute's descriptions from the local file
def extract_attributes_description(schema, attributesDescription_path):

    if attributesDescription_path is None:
        return []

    with open(attributesDescription_path, 'r') as f:
        data = json.load(f)

    query_tables = set(schema.keys())

    matched_attribute = []

    for item in data["attributes"]:

        table = item["table"]
        table_name = table["name"]

        if table_name in query_tables:
            matched_attribute.append(table)

    return matched_attribute



def parse_annotations(file_path, db_path, examples_path, attribute_desc_path):

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
            "examples": extract_examples(schema, examples_path),
            "attribute_description": extract_attributes_description(schema, attribute_desc_path)
        })

    return results