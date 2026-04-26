from groq import Groq
from config import API_KEY

import time


client = Groq(api_key=API_KEY)

def call_llm(prompt, model_name):

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a SQL expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def text_to_sql_prompt(input_data):

    results = []

    for item in input_data:
        nl = item["nl"]
        tables = item["tables"]
        table_schemas = item["table_schemas"]

        prompt = f"""
        You are a system that translates natural language questions into SQL queries.

        You are given:
        - A natural language question (nl)
        - A list of relevant tables (tables)
        - The schema of those tables (table_schemas)

        Rules:
        - Use ONLY the provided tables
        - Return ONLY the SQL query (no explanation)
        - If the question cannot be answered with the provided tables, return "NO QUERY" (no further explanation)

        Input:
        nl: {nl}
        tables: {tables}
        schema: {table_schemas}
        """

        try:
            start = time.time()
            sql_llama = call_llm(prompt, "llama-3.3-70b-versatile")
            time_llama = time.time() - start

            start = time.time()
            sql_gptoss = call_llm(prompt, "openai/gpt-oss-120b")
            time_gptoss = time.time() - start

        except Exception as e:
            print("Errore:", e)
            sql_llama = sql_gptoss = ""
            time_llama = time_gptoss = 0

        results.append({
            "nl": nl,
            "tables": tables,
            "schema": table_schemas,
            "prompt": prompt,
            "predictions": {
                "llama-3.3-70b-versatile": sql_llama,
                "gpt-oss-120b": sql_gptoss
            },
            "latency": {
                "llama-3.3-70b-versatile": time_llama,
                "gpt-oss-120b": time_gptoss
            }
        })


    return results