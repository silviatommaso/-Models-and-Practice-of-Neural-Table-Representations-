import json
import os
from dotenv import load_dotenv

from annotation_parser import parse_annotations
from llm_requests import prompt
from normalizer import normalize_sql, normalize_ground_truth
from questioning import execute_llm_queries, execute_ground_truth_queries
from result_formatter import reorder_file, to_tuple_format
from evaluation import evaluate


load_dotenv()
file_path = os.getenv("BOOK_1_ANNOTATION_PATH")
db_path = os.getenv("DB__BOOK_1_PATH")

##########################################################################
# # - Parsing annotations.json file 
# #       - queries
# #       - sql
# # - Schema extraction from schema.sql 

results = parse_annotations(file_path, db_path)

with open("json/book_1/book1_queries.json", "w") as f:
    json.dump(results, f, indent=4)
##########################################################################

##########################################################################
# # - Prompt LLM for SQL query generation:
llm_TTSQL, llm_QA = prompt(results)

with open("json/book_1/book1_predictions_QA.json", "w") as f:
    json.dump(llm_QA, f, indent=4)

with open("json/book_1/book1_predictions_TTSQL.json", "w") as f:
    json.dump(llm_TTSQL, f, indent=4)
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
