from groq import Groq
from config import API_KEY
import time

client = Groq(api_key=API_KEY)


# -----------------------
# UTILS
# -----------------------

def clean_sql(output):
    if not output:
        return output
    return (
        output.replace("```sql", "")
        .replace("```", "")
        .strip()
    )


def build_messages_TSQL(nl, tables, table_schemas, primary_keys, foreign_keys):
    return [
        {
            "role": "system",
            "content": """You are a system that translates natural language questions into SQL queries.

            Rules:
            - Use ONLY the provided tables
            - Return ONLY the SQL query (no explanation)
            - If the question cannot be answered with the provided tables, return "NO QUERY"
            """
        },
        {
            "role": "user",
            "content": f"""
            
            nl: {nl}
            tables: {tables}
            schema: {table_schemas}
            primary_keys: {primary_keys}
            foreign_keys: {foreign_keys}
            """
        }
    ]


def call_llm(messages, model_name):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0
    )

    usage = getattr(response, "usage", None)

    tokens = {
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    } if usage else None

    content = response.choices[0].message.content.strip()
    content = clean_sql(content)

    return content, tokens


# -----------------------
# MAIN FUNCTION
# -----------------------

def text_to_sql_prompt(input_data):

    results = []

    for item in input_data:
        nl = item["nl"]
        tables = item["tables"]
        table_schemas = item["table_schemas"]
        primary_keys = item["primary_keys"]
        foreign_keys = item["foreign_keys"]

        messages = build_messages_TSQL(
            nl, tables, table_schemas, primary_keys, foreign_keys
        )

        try:
            # LLaMA
            start = time.time()
            sql_llama, tokens_llama = call_llm(
                messages, "llama-3.3-70b-versatile"
            )
            time_llama = time.time() - start

            # GPT-OSS
            start = time.time()
            sql_gptoss, tokens_gptoss = call_llm(
                messages, "openai/gpt-oss-120b"
            )
            time_gptoss = time.time() - start

        except Exception as e:
            print("Errore:", e)
            sql_llama = None
            sql_gptoss = None
            tokens_llama = None
            tokens_gptoss = None
            time_llama = 0
            time_gptoss = 0

        results.append({
            "nl": nl,
            "tables": tables,
            "schema": table_schemas,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "predictions": {
                "llama-3.3-70b-versatile": sql_llama,
                "gpt-oss-120b": sql_gptoss
            },
            "latency": {
                "llama-3.3-70b-versatile": time_llama,
                "gpt-oss-120b": time_gptoss
            },
            "tokens": {
                "llama-3.3-70b-versatile": tokens_llama,
                "gpt-oss-120b": tokens_gptoss
            }
        })

    return results