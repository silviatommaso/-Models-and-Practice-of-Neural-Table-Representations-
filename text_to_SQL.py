import json
import os
from dotenv import load_dotenv

from annotation_parser import parse_annotations
from schema_reader import get_schema, get_primary_keys, get_foreign_keys
from llm_requests import text_to_sql_prompt
from sql_normalizer import normalize_sql, normalize_ground_truth
from sql_questioning import execute_llm_queries, execute_ground_truth_queries
from result_formatter import reorder_file, to_tuple_format
from evaluation import evaluate


load_dotenv()
file_path = os.getenv("BOOK_1_ANNOTATION_PATH")
db_path = os.getenv("DB__BOOK_1_PATH")

# ----------------------------------------------------------------------
# # TEXT-TO-SQL PIPELINE:
# ----------------------------------------------------------------------

##########################################################################
# # - Parsing annotations.json file 
# #       - queries
# #       - sql

results = parse_annotations(file_path)
##########################################################################

##########################################################################
# # - schema extraction from schema.sql 

for item in results:
    tables = item["tables"]
    schema = get_schema(tables, db_path)
    primary_keys = get_primary_keys(tables, db_path)
    foreign_keys = get_foreign_keys(tables, db_path)

    item["table_schemas"] = schema
    item["primary_keys"] = primary_keys
    item["foreign_keys"] = foreign_keys

with open("json/book_1_keys/book1_queries.json", "w") as f:
    json.dump(results, f, indent=4)
##########################################################################

##########################################################################
# # - Prompt LLM for SQL query generation:
llm_results = text_to_sql_prompt(results)
##########################################################################

##########################################################################
# # - Response normalization 

data = llm_results

for item in data:

    for model in item["predictions"]:
        item["predictions"][model] = normalize_sql(
            item["predictions"][model]
        )

with open("json/book_1_keys/book1_predictions.json", "w") as f:
    json.dump(data, f, indent=4)
##########################################################################

##########################################################################
# # - Execute the generated SQL queries on the database
with open("json/book_1_keys/book1_predictions.json", 'r') as f:
    data = json.load(f)

    queries = []

    for item in data:
        queries.append({
            "nl": item["nl"],
            "llama_sql": item["predictions"].get("llama-3.3-70b-versatile", ""),
            "gpt_sql": item["predictions"].get("gpt-oss-120b", "")
        })

sqlite_results = execute_llm_queries(db_path, queries)

with open("json/book_1_keys/book1_sqlite_response.json", "w") as f:
    json.dump(sqlite_results, f, indent=4)
###########################################################################






# -----------------------------------
# # GROUND TRUTH REFINEMENT: 
# -----------------------------------

#################################################################################################################
# # - Normalize the SQL queries in the annotations.json file to create a clean ground truth for evaluation.
ground_truth = normalize_ground_truth(file_path)

with open("json/book_1_keys/book1_ground_truth.json", "w") as f:
    json.dump(ground_truth, f, indent=4)
#################################################################################################################

#################################################################################################################
# # - Execute the ground truth SQL queries on the database
data = ground_truth

queries = []

for item in data:
    queries.append({
        "nl": item["nl"],
        "sql": item["sql"]
    })

sqlite_results = execute_ground_truth_queries(db_path, queries)

with open("json/book_1_keys/book1_ground_truth_sqlite_response.json", "w") as f:
    json.dump(sqlite_results, f, indent=4)
################################################################################################################






# -----------------------------------
# # COMPARISON AND EVALUATION: 
# -----------------------------------

#############################################################################################################################################################################################################################################################
# # - Normalize the keys of the SQL query results and reorder them according to the schema order extracted from the ground truth data, to ensure a fair comparison between the predicted results and the ground truth results.
book1_sqlite_tuples = reorder_file("json/book_1_keys/book1_sqlite_response.json", "json/book_1/book1_ground_truth_sqlite_response.json")

# with open("json/book_1/book1_sqlite_tuples.json", "w") as f:
#     json.dump(book1_sqlite_tuples, f, indent=4)
#############################################################################################################################################################################################################################################################

#########################################################################################################################################################
# # - Transforming the ground truth into a list of tuples
ground_truth_tuples = to_tuple_format("json/book_1_keys/book1_ground_truth_sqlite_response.json")

# with open("json/book_1/book1_ground_truth_tuples.json", "w") as f:
#     json.dump(ground_truth_tuples, f, indent=4)
#########################################################################################################################################################

#########################################################################################################################################################
# # - Comparing the groundtruth and the predicted results
evaluation = evaluate(book1_sqlite_tuples, ground_truth_tuples)

with open("json/book_1_keys/book1_evaluation.json", "w") as f:
    json.dump(evaluation, f, indent=4)
#########################################################################################################################################################
