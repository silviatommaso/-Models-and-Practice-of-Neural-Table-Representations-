from groq import Groq
from config import API_KEY
import time


client = Groq(api_key=API_KEY)

PAUSE_BETWEEN_MODELS = 5
PAUSE_BETWEEN_QUERIES = 20



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



########################################################################################################################################################################################################################################################################################################
########################################################################################################################################################################################################################################################################################################



# -----------------------
# TEXT-TO-SQL
# -----------------------

def build_messages_TSQL(nl, table_schemas, primary_keys, foreign_keys):
    return [
        {
            "role": "system",
            "content": """You are a system that translates natural language questions into SQL queries.

            Rules:
            - Use ONLY the provided tables
            - Return ONLY the SQL query (no explanation)
            - Be sure to select ONLY the columns that answer the question
            - If the question cannot be answered with the provided tables, return "NO QUERY"

            
            Examples:

            Question:
            Orders whose total amount is less than 50
            

            Table1: "BOOK"
            Attributes:
                "ISBN",
                "Title",
                "Author",
                "PurchasePrice",
                "SalePrice"

            Table2: "BOOKS_ORDER"
            Attributes: 
                "ISBN",
                "IdOrder",
                "amount"


            Answer:
            SELECT IdOrder, (PurchasePrice*amount) AS TOTAL FROM BOOKS_ORDER NATURAL JOIN BOOK WHERE (PurchasePrice*amount)<50;



            Question:
            Orders with more then one copy

            Table1: "BOOKS_ORDER"
            Attributes: 
                "ISBN",
                "IdOrder",
                "amount"

            Answer:
            SELECT IdOrder, amount FROM BOOKS_ORDER WHERE amount>1;



            Question:
            Books the store purchased for more than 10 and less than 15

            Table1: "BOOK"
            Attributes:
                "ISBN",
                "Title",
                "Author",
                "PurchasePrice",
                "SalePrice"

            Answer:
            SELECT Title, ISBN, PurchasePrice FROM BOOK WHERE PurchasePrice>10 AND PurchasePrice<15;
            """
        },
        {
            "role": "user",
            "content": f"""
            
            nl: {nl}
            schema: {table_schemas}
            primary_keys: {primary_keys}
            foreign_keys: {foreign_keys}
            """
        }
    ]


# -----------------------
# QUESTION-ANSWER
# -----------------------

def build_messages_QA(nl, table_serialized, primary_keys, foreign_keys):
    return [
        {
            "role": "system",
            "content": """You are a system that search for the answer of a natural language question in a serialized database format (TABLE: attribute: type: value).

            Rules:
            - Use ONLY the provided serialized tables to find the answer to the question.
            - Be sure to select ONLY the columns that answer the question
            - Return ONLY the rows you find (no explanation) in the format "attribute: type: value | attribute: type: value | ...". If multiple rows are found, separate them with a newline character.
            - If the question cannot be answered with the provided tables, return "NO ANSWER"

            
            Helpful information:

            Table1: AUTHOR
            Attributes: 
                - idAuthor (unique author id)  
                - Name (Name of the author) 

            Table2: AUTHOR BOOK 
            Attributes:
                - ISBN (Internationl Standard Book Number, which uniquely identifies a book edition)
                - Author (the id author)
            
            Table3: BOOK 
            Attributes:
                - ISBN (Internationl Standard Book Number, which uniquely identifies a book edition)
                - Title (Book's title)
                - Author (pubblication date)
                - PurchasePrice (price per single book paid by the bookstore when buying from supplier)
                - SalePrice (price per single book paid by customers to the bookstore)

            Table4: BOOKS_ORDER
            Attributes:
                - ISBN (Internationl Standard Book Number, which uniquely identifies a book edition)
                - IdOrder (unique order identifier)
                - amount (amount of books per order)

            Table5: CLIENT
            Attributes: 
                - IdClient (unique client identifier)
                - Name (Client name)
                - Address (client's address)
                - NumCC (Card Credit Number)

            Table6: ORDERS 
            Attributes: 
                - IdOrder (unique order identifier)
                - IdClient (unique client identifier)
                - DateOrder (Date the order has been made)
                - DateExped (shipping date)
            """
        },
        {
            "role": "user",
            "content": f"""
            
            nl: {nl}
            serialized_table: {table_serialized}
            primary_keys: {primary_keys}
            foreign_keys: {foreign_keys}
            """
        }
    ]



########################################################################################################################################################################################################################################################################################################
########################################################################################################################################################################################################################################################################################################


def result_definer(messages, nl, tables, results):

    try:
            
        # LLaMA TTSQL
        start = time.time()
        llama_asw, tokens_llama = call_llm(messages, "llama-3.3-70b-versatile")
        time_llama = time.time() - start

        # pause between the two models to avoid interference
        time.sleep(PAUSE_BETWEEN_MODELS)
        
        # GPT-OSS TTSQL
        start = time.time()
        gptoss_asw, tokens_gptoss = call_llm(messages, "openai/gpt-oss-120b")
        time_gptoss = time.time() - start

    except Exception as e:
            print("Error:", e)
            llama_asw = None
            gptoss_asw = None
            tokens_llama = None
            tokens_gptoss = None
            time_llama = 0
            time_gptoss = 0


    results.append({
            "nl": nl,
            "tables": tables,
            "predictions": {
                "llama-3.3-70b-versatile": llama_asw,
                "gpt-oss-120b": gptoss_asw
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

def prompt(input_data):

    results_QA = []
    results_TTSQL = []

    for item in input_data:
        nl = item["nl"]
        tables = item["tables"]
        table_schemas = item["schema"]
        table_serialized = item["table_serialized"]
        primary_keys = item["primary_keys"]
        foreign_keys = item["foreign_keys"]

        messages_TTSQL = build_messages_TSQL(nl, table_schemas, primary_keys, foreign_keys)
        results_TTSQL = result_definer(messages_TTSQL, nl, tables, results_TTSQL)

        time.sleep(PAUSE_BETWEEN_QUERIES)
        
        messages_QA = build_messages_QA(nl, table_serialized, primary_keys, foreign_keys)   
        results_QA = result_definer(messages_QA, nl, tables, results_QA)

        time.sleep(PAUSE_BETWEEN_QUERIES)


    return results_TTSQL, results_QA