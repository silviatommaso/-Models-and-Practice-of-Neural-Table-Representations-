import json


# function to extract the schema order for each query from the ground truth data predictions
def build_schema_map(schema_file):

    with open(schema_file, 'r') as f:
        schema_data = json.load(f)

    schema_map = {}

    for item in schema_data:

        nl = item["nl"]
        sql = item["sql"]
        predictions = item.get("prediction", [])

        if not predictions:
            schema_map[nl] = []
            schema_map[sql] = []
            continue


        if isinstance(predictions, list):
            first_row = predictions[0] if predictions else {}
        # elif isinstance(predictions, dict):
        #     first_row = predictions
        else:
            first_row = {}

        schema_order = [k.upper() for k in first_row.keys()]

        schema_map[nl] = schema_order

    return schema_map



def normalize_keys(row):
    return {k.upper(): v for k, v in row.items()}



def order_row(row, schema_order):

    row = normalize_keys(row)

    ordered = []

    for attr in schema_order:
        value = row.get(attr)

        if value is None:
            ordered.append("NULL")
        else:
            ordered.append(str(value))

    
    extra_attrs = [k for k in row.keys() if k not in schema_order]

    for attr in extra_attrs:
        value = row[attr]
        ordered.append(str(value) if value is not None else "NULL")

    return ordered


# function to reorder the keys of the SQL query results according to the schema order extracted from the ground truth data
def reorder_file(input_file, schema_file):

    with open(input_file, 'r') as f:
        data = json.load(f)

    schema_map = build_schema_map(schema_file)
    new_data = []

    for item in data:

        nl = item["nl"]
        # sql_llama = item["sql_llama"]
        # sql_gpt = item["sql_gpt"]

        llama = item.get("llama", [])
        gpt = item.get("gpt", [])

        # if the predictions are not lists (e.g., in case of errors), we set them to empty lists to avoid issues during reordering
        # llama = llama if isinstance(llama, list) else []
        # gpt = gpt if isinstance(gpt, list) else []

        schema_order = schema_map.get(nl, [])


        ordered_llama = [order_row(row, schema_order) for row in llama]

        ordered_gpt = [order_row(row, schema_order) for row in gpt]

        new_data.append({
            "nl": nl,
            # "sql_llama": sql_llama,
            "llama": ordered_llama,
            # "sql_gpt": sql_gpt,
            "gpt": ordered_gpt
        })

    return new_data



# function to convert the predictions from list of dicts format to list of tuples format, handling also the case of errors where the prediction is a dict instead of a list of dicts
def to_tuple_format(input_file):

    with open(input_file, 'r') as f:
        data = json.load(f)

    new_data = []

    for item in data:

        nl = item["nl"]
        sql = item["sql"]
        prediction = item.get("prediction", [])

        # caso errore
        if isinstance(prediction, dict):
            new_prediction = prediction
        else:
            new_prediction = [
                tuple(str(v) if v is not None else "NULL" for v in row.values())
                for row in prediction
            ]

        new_data.append({
            "nl": nl,
            "sql": sql,
            "prediction": new_prediction
        })

    return new_data