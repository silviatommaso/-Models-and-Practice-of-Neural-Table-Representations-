import json

from annotation_parser import parse_annotations
from schema_reader import get_schema
from llm_requests import text_to_sql_prompt
from sql_normalizer import normalize_sql, normalize_ground_truth
from sql_questioning import execute_llm_queries, execute_ground_truth_queries
from result_formatter import reorder_file



# ----------------------------------------------------------------------
# # TEXT-TO-SQL PIPELINE:
# ----------------------------------------------------------------------

##########################################################################
# # - Parsing annotations.json file 
# #       - queries
# #       - sql

# results = parse_annotations()
##########################################################################

##########################################################################
# # - schema extraction from schema.sql 
# for item in results:
#     tables = item["tables"]
#     schema = get_schema(tables)
#     item["table_schemas"] = schema

# with open("json/book1_queries.json", "w") as f:
#     json.dump(results, f, indent=4)
##########################################################################

##########################################################################
# # - Prompt LLM for SQL query generation:
# llm_results = text_to_sql_prompt(results)
##########################################################################

##########################################################################
# # - Response normalization 

# data = llm_results

# for item in data:

#     for model in item["predictions"]:
#         item["predictions"][model] = normalize_sql(
#             item["predictions"][model]
#         )

# with open("json/book1_predictions.json", "w") as f:
#     json.dump(data, f, indent=4)
##########################################################################

##########################################################################
# # - Execute the generated SQL queries on the database
# with open("json/book1_predictions.json", 'r') as f:
#     data = json.load(f)

#     queries = []

#     for item in data:
#         queries.append({
#             "nl": item["nl"],
#             "llama_sql": item["predictions"].get("llama-3.3-70b-versatile", ""),
#             "gpt_sql": item["predictions"].get("gpt-oss-120b", "")
#         })

# sqlite_results = execute_llm_queries(queries)

# with open("json/book1_sqlite_response.json", "w") as f:
#     json.dump(sqlite_results, f, indent=4)
###########################################################################






# -----------------------------------
# # GROUND TRUTH REFINEMENT: 
# -----------------------------------

#################################################################################################################
# # - Normalize the SQL queries in the annotations.json file to create a clean ground truth for evaluation.
# ground_truth = normalize_ground_truth()

# with open("json/book1_ground_truth.json", "w") as f:
#     json.dump(ground_truth, f, indent=4)
#################################################################################################################

#################################################################################################################
# # - After a manual review, execute the ground truth SQL queries on the database
# with open("json/book1_ground_truth.json", 'r') as f:
#     data = json.load(f)

#     queries = []

#     for item in data:
#         queries.append({
#             "nl": item["nl"],
#             "sql": item["sql"]
#         })

# sqlite_results = execute_ground_truth_queries(queries)

# with open("json/book1_ground_truth_sqlite_response.json", "w") as f:
#     json.dump(sqlite_results, f, indent=4)
################################################################################################################






# -----------------------------------
# # COMPARISON AND EVALUATION: 
# -----------------------------------

#############################################################################################################################################################################################################################################################
# # - Normalize the keys of the SQL query results and reorder them according to the schema order extracted from the ground truth data, to ensure a fair comparison between the predicted results and the ground truth results.
output = reorder_file("json/book1_sqlite_response.json", "json/book1_ground_truth_sqlite_response.json")

with open("json/book1_sqlite_response_reordered.json", "w") as f:
    json.dump(output, f, indent=4)
#############################################################################################################################################################################################################################################################

#########################################################################################################################################################
# # - Transform the ground truth list of dictionaries into a list of tuples (nl, sql) for easier comparison with the predicted results.
# output = reorder_file("json/book1_sqlite_response.json", "json/book1_ground_truth_sqlite_response.json")

# with open("json/book1_sqlite_response_reordered.json", "w") as f:
#     json.dump(output, f, indent=4)
#########################################################################################################################################################
