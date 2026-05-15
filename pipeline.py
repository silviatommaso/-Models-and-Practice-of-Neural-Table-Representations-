import os
from dotenv import load_dotenv

from file_load import read_file, write_file
from annotation_parser import parse_annotations
from llm_requests import prompt
from normalizer import normalize, normalize_ground_truth
from questioning import execute_llm_queries, execute_ground_truth_queries
from result_formatter import remove_attributes, remove_attributes_ground_truth
from evaluation import evaluate


load_dotenv()
file_path = os.getenv("BOOK_1_ANNOTATION_PATH")
db_path = os.getenv("DB__BOOK_1_PATH")
examples_path = os.getenv("BOOK_1_EXAMPLES_PATH")
attribute_description_path = os.getenv("BOOK_1_ATTRIBUTE_DESC_PATH")


##########################################################################
# # - Parsing annotations.json file 
# #       - queries
# #       - sql
# # - Schema extraction from schema.sql 

queries = parse_annotations(file_path, db_path, examples_path, attribute_description_path)

write_file(queries, "json/book_1/book1_queries.json")
##########################################################################

##########################################################################
# # - Prompt LLM for SQL query generation:
llm_TTSQL, llm_QA = prompt(queries)
##########################################################################

##########################################################################
# # - Response normalization 
normalized_QA, normalized_TTSQL = normalize(llm_QA, llm_TTSQL)

write_file(normalized_QA, "json/book_1/book_1_QA_fewshot/book1_llm_predictions_QA.json")
write_file(normalized_TTSQL, "json/book_1/book_1_TTSQL_fewshot/book1_llm_predictions_TTSQL.json")
########################################################################

##########################################################################
# # - Execute the generated TTSQL queries on the database
with open('json/book_1/book_1_TTSQL_fewshot/book1_llm_predictions_TTSQL.json', 'r') as f:
    normalized_TTSQL = read_file("json/book_1/book_1_TTSQL_fewshot/book1_llm_predictions_TTSQL.json")
sqlite_TTSQL = execute_llm_queries(db_path, normalized_TTSQL)

write_file(sqlite_TTSQL, "json/book_1/book_1_TTSQL_fewshot/book1_sqlite_response.json")
###########################################################################




# -----------------------------------
# # GROUND TRUTH REFINEMENT: 
# -----------------------------------

#################################################################################################################
# # - Normalize the SQL queries in the annotations.json file to create a clean ground truth for evaluation.
ground_truth = normalize_ground_truth(file_path)

write_file(ground_truth, "json/book_1/book_1_ground_truth.json")
#################################################################################################################

#################################################################################################################
# # - Execute the ground truth SQL queries on the database

queries = []

for item in ground_truth:
    queries.append({
        "nl": item["nl"],
        "sql": item["sql"]
    })

sqlite_ground_truth = execute_ground_truth_queries(db_path, queries)

write_file(sqlite_ground_truth, "json/book_1/book_1_ground_truth_sqlite_response.json")
################################################################################################################






# -----------------------------------
# # COMPARISON AND EVALUATION: 
# -----------------------------------

#############################################################################################################################################################################################################################################################
# # - Normalize the keys of the SQL query results and reorder them according to the schema order extracted from the ground truth data, to ensure a fair comparison between the predicted results and the ground truth results.
gt = read_file("json/book_1/book_1_ground_truth_sqlite_response.json")
data_TTSQL = read_file("json/book_1/book_1_TTSQL_fewshot/book1_sqlite_response.json")
data_QA = read_file("json/book_1/book_1_QA_fewshot/book1_llm_predictions_QA.json")

ground_truth_formatted = remove_attributes_ground_truth(gt)
TTSQL_formatted = remove_attributes(data_TTSQL)
QA_formatted = remove_attributes(data_QA)
#######################################################################################################################################################################################################################################################################

#########################################################################################################################################################
# # - Comparing the groundtruth and the predicted results
evaluation_QA = evaluate(QA_formatted, ground_truth_formatted)
evaluation_TTSQL = evaluate(TTSQL_formatted, ground_truth_formatted)

write_file(evaluation_QA, "json/book_1/book_1_QA_fewshot/book1_evaluation_QA.json")
write_file(evaluation_TTSQL, "json/book_1/book_1_TTSQL_fewshot/book1_evaluation_TTSQL.json")
#########################################################################################################################################################