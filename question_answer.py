import json
import os
from dotenv import load_dotenv

from annotation_parser import parse_annotations
from llm_requests import question_answer_prompt
from normalizer import normalize_sql, normalize_ground_truth, normalize_llm_output
from questioning import execute_llm_queries, execute_ground_truth_queries
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
# # - Schema extraction from schema.sql 

# results = parse_annotations(file_path, db_path)

# with open("json_QA/book_1/book1_queries.json", "w") as f:
#     json.dump(results, f, indent=4)
##########################################################################

##########################################################################
# - Prompt LLM for SQL query generation:
# llm_results = question_answer_prompt(results)

# with open("json_QA/book_1/book1_predictions_llm.json", "w") as f:
#     json.dump(llm_results, f, indent=4)
##########################################################################

##########################################################################
# # - Response normalization 

with open("json_QA/book_1/book1_predictions_llm.json", 'r') as f:
    data = json.load(f)

results = []

for item in data:

    new_item = {
        "nl": item["nl"],
        "llama": [],
        "gpt": []
    }

    new_item["llama"] = normalize_llm_output(item.get("predictions", {}).get("llama-3.3-70b-versatile", []))
    new_item["gpt"] = normalize_llm_output(item.get("predictions", {}).get("gpt-oss-120b", []))

    results.append(new_item)

with open("json_QA/book_1/book1_predictions_llm_normalized.json", "w") as f:
    json.dump(results, f, indent=4)
########################################################################




# -----------------------------------
# # GROUND TRUTH REFINEMENT: 
# -----------------------------------

#################################################################################################################
# # - Normalize the SQL queries in the annotations.json file to create a clean ground truth for evaluation.
ground_truth = normalize_ground_truth(file_path)

with open("json_QA/book_1/book1_ground_truth.json", "w") as f:
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

with open("json_QA/book_1/book1_ground_truth_sqlite_response.json", "w") as f:
    json.dump(sqlite_results, f, indent=4)
######################################################################################################################






# -----------------------------------
# # COMPARISON AND EVALUATION: 
# -----------------------------------

#############################################################################################################################################################################################################################################################
# # - Normalize the keys of the SQL query results and reorder them according to the schema order extracted from the ground truth data, to ensure a fair comparison between the predicted results and the ground truth results.
book1_sqlite_tuples = reorder_file("json_QA/book_1/book1_predictions_llm_normalized.json", "json_QA/book_1/book1_ground_truth_sqlite_response.json")

with open("json_QA/book_1/book1_sqlite_tuples.json", "w") as f:
    json.dump(book1_sqlite_tuples, f, indent=4)
#############################################################################################################################################################################################################################################################

#########################################################################################################################################################
# # - Transforming the ground truth into a list of tuples
ground_truth_tuples = to_tuple_format("json_QA/book_1/book1_ground_truth_sqlite_response.json")

# with open("json_QA/book_1/book1_ground_truth_tuples.json", "w") as f:
#     json.dump(ground_truth_tuples, f, indent=4)
#########################################################################################################################################################

#########################################################################################################################################################
# # - Comparing the groundtruth and the predicted results
evaluation = evaluate(book1_sqlite_tuples, ground_truth_tuples)

with open("json_QA/book_1/book1_evaluation.json", "w") as f:
    json.dump(evaluation, f, indent=4)
#########################################################################################################################################################
