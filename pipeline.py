import json
import os
from dotenv import load_dotenv

from annotation_parser import parse_annotations
from llm_requests import prompt
from normalizer import normalize, normalize_ground_truth
from questioning import execute_llm_queries, execute_ground_truth_queries
from result_formatter import remove_attributes, remove_attributes_ground_truth
from evaluation import evaluate


load_dotenv()
file_path = os.getenv("BOOK_1_ANNOTATION_PATH")
db_path = os.getenv("DB__BOOK_1_PATH")

##########################################################################
# # - Parsing annotations.json file 
# #       - queries
# #       - sql
# # - Schema extraction from schema.sql 

# results = parse_annotations(file_path, db_path)

# with open("json/book_1/book1_queries.json", "w") as f:
#     json.dump(results, f, indent=4)
##########################################################################

##########################################################################
# # - Prompt LLM for SQL query generation:
# llm_TTSQL, llm_QA = prompt(results)

# with open("json/book_1/book_1_QA/book1_llm_QA.json", "w") as f:
#     json.dump(llm_QA, f, indent=4)

# with open("json/book_1/book_1_TTSQL/book1_llm_TTSQL.json", "w") as f:
#     json.dump(llm_TTSQL, f, indent=4)
##########################################################################

##########################################################################
# # - Response normalization 

# with open("json/book_1/book_1_QA/book1_llm_QA.json", 'r') as f:
#     data_QA = json.load(f)

# with open("json/book_1/book_1_TTSQL/book1_llm_TTSQL.json", 'r') as f:
#     data_TTSQL = json.load(f)


# normalized_QA, normalized_TTSQL = normalize(data_QA, data_TTSQL)

# with open("json/book_1/book_1_QA/book1_predictions_QA.json", "w") as f:
#     json.dump(normalized_QA, f, indent=4)

# with open("json/book_1/book_1_TTSQL/book1_predictions_TTSQL.json", "w") as f:
#     json.dump(normalized_TTSQL, f, indent=4)
########################################################################

##########################################################################
# # - Execute the generated SQL queries on the database
# with open("json/book_1/book_1_TTSQL/book1_predictions_TTSQL.json", 'r') as f:
#     data = json.load(f)

# sqlite_results = execute_llm_queries(db_path, data)

# with open("json/book_1/book_1_TTSQL/book1_sqlite_response.json", "w") as f:
#     json.dump(sqlite_results, f, indent=4)
###########################################################################




# -----------------------------------
# # GROUND TRUTH REFINEMENT: 
# -----------------------------------

#################################################################################################################
# # - Normalize the SQL queries in the annotations.json file to create a clean ground truth for evaluation.
ground_truth = normalize_ground_truth(file_path)

with open("json/book_1/book1_ground_truth.json", "w") as f:
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

with open("json/book_1/book1_ground_truth_sqlite_response.json", "w") as f:
    json.dump(sqlite_results, f, indent=4)
################################################################################################################






# -----------------------------------
# # COMPARISON AND EVALUATION: 
# -----------------------------------

#############################################################################################################################################################################################################################################################
# # - Normalize the keys of the SQL query results and reorder them according to the schema order extracted from the ground truth data, to ensure a fair comparison between the predicted results and the ground truth results.
with open("json/book_1/book_1_TTSQL/book1_sqlite_response.json", 'r') as f:
    data_TTSQL = json.load(f)
with open("json/book_1/book_1_QA/book1_predictions_QA.json", 'r') as f:
    data_QA = json.load(f)

ground_truth_formatted = remove_attributes_ground_truth(sqlite_results)
TTSQL_formatted = remove_attributes(data_TTSQL)
QA_formatted = remove_attributes(data_QA)

with open("json/book_1/book1_ground_truth_formatted.json", "w") as f:
    json.dump(ground_truth_formatted, f, indent=4)
with open("json/book_1/book_1_QA/book1_formatted_QA.json", "w") as f:
    json.dump(QA_formatted, f, indent=4)
with open("json/book_1/book_1_TTSQL/book1_formatted_TTSQL.json", "w") as f:
    json.dump(TTSQL_formatted, f, indent=4)
#######################################################################################################################################################################################################################################################################

#########################################################################################################################################################
# # - Comparing the groundtruth and the predicted results
evaluation_QA = evaluate(QA_formatted, ground_truth_formatted)
evaluation_TTSQL = evaluate(TTSQL_formatted, ground_truth_formatted)

with open("json/book_1/book_1_QA/book1_evaluation.json", "w") as f:
    json.dump(evaluation_QA, f, indent=4)
with open("json/book_1/book_1_TTSQL/book1_evaluation_TTSQL.json", "w") as f:
    json.dump(evaluation_TTSQL, f, indent=4)
#########################################################################################################################################################
