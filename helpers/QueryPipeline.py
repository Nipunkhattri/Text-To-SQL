from llama_index.core.query_engine import NLSQLTableQueryEngine
from flask import g, current_app
from llama_index.core import SQLDatabase, VectorStoreIndex, ServiceContext
from llama_index.llms.gemini import Gemini
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from sqlalchemy import MetaData, text, create_engine
from sqlalchemy.engine import reflection
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core.query_pipeline import QueryPipeline, InputComponent, FnComponent
from datetime import datetime
import re
from llama_index.core.prompts import PromptTemplate

def get_db_schema(db_url):
    engine = create_engine(db_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    inspector = reflection.Inspector.from_engine(engine)
    inspector = reflection.Inspector.from_engine(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = {col['name']: col['type'] for col in columns}
    return schema

def extract_sql_query(prompt):
    # Use the LLM to generate the SQL query based on the prompt
    llm = Gemini(model_name='models/gemini-pro', api_key='AIzaSyDHLca8_D4lBazOgveuzP31cssj5ETaSaM')
    response = llm.complete(prompt)
    sql_query = response.text.strip()
    sql_query = re.sub(r'```sql|```', '', sql_query).strip()
    print(sql_query)
    return sql_query

# Function to generate prompt from schema and query
def generate_prompt(query_str, db_schema):
    schema_str = ""
    for table, columns in db_schema.items():
        schema_str += f"Table: {table}\n"
        for column, data_type in columns.items():
            schema_str += f"  - {column}: {data_type}\n"
        schema_str += "\n"

    # Construct the prompt
    prompt = f"""You are an AI assistant trained to generate SQL queries based on natural language questions and database schemas. Your task is to create a SQL query that answers the given question using the provided database schema.

    Database Schema:
    {schema_str}

    User Question: {query_str}

    Please generate a SQL query that answers the user's question based on the given database schema. The query should be correct, efficient, and follow SQL best practices. If you need to make any assumptions, please state them clearly.

    SQL Query:
    """
    return prompt

def run_sql_query(db_url, sql_query) -> str:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        # check for empty result
        if result.rowcount == 0:
            query_result = "No results found"
        else:
            query_result = "\n".join([str(row) for row in result.fetchall()])

    print(query_result)
    return query_result

def QueryLLM(query, db_url):
    llm = Gemini(model_name='models/gemini-pro', api_key='AIzaSyDHLca8_D4lBazOgveuzP31cssj5ETaSaM')
    input_component = InputComponent()

    # Use to get the schema
    db_schema_tool = FnComponent(fn=get_db_schema) 

    # Use to generate the prompt
    generate_prompt_tool = FnComponent(fn=generate_prompt)

    # Used to get the sql query
    extract_sql_query_intermediate = FnComponent(fn=extract_sql_query)

    # Use to run the Sql query 
    sql_result_tool = FnComponent(fn=run_sql_query)

    # refine sql query result
    refine_query_result_temp = (
        "You are a data analyst and you have given a query and sql result"
        "You have to gave the sql result in the readable format"
        "\n"
        "{query_str}"
        "\n"
        "The query result is as follows:"
        "\n"
        "{sql_result}"
        "\n"
        "Combine the result for more readability. Gave result in string form"
        "\n"
        "response:"
    )
    refine_query_result_temp = PromptTemplate(refine_query_result_temp)

    # Query Pipeline
    p = QueryPipeline(verbose=True)
    p.add_modules(
        {
            "input_component": input_component,
            "db_schema_tool": db_schema_tool,
            "generate_prompt_tool": generate_prompt_tool,
            "extract_sql_query_intermediate": extract_sql_query_intermediate,
            "sql_result_tool": sql_result_tool,
            "refine_query_result_temp": refine_query_result_temp,
            "final_response": llm,
        }
    )
    p.add_link("input_component", "db_schema_tool", src_key="db_url",dest_key="db_url")
    p.add_link("db_schema_tool", "generate_prompt_tool", src_key="output" ,dest_key="db_schema")
    p.add_link("input_component", "generate_prompt_tool", src_key="query_str" ,dest_key="query_str")
    p.add_link("generate_prompt_tool", "extract_sql_query_intermediate",src_key='output',dest_key="prompt")
    p.add_link("extract_sql_query_intermediate","sql_result_tool",src_key="output",dest_key="sql_query")
    p.add_link("input_component","sql_result_tool",src_key="db_url",dest_key="db_url")
    p.add_link("input_component", "refine_query_result_temp", src_key="query_str",dest_key="query_str")
    p.add_link("sql_result_tool", "refine_query_result_temp", src_key="output",dest_key="sql_result")    
    p.add_link("refine_query_result_temp", "final_response")

    # Execute the pipeline with the provided query and db_url
    response = p.run(query_str=query, db_url=db_url)
    print(response)
    return response