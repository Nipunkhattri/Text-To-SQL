from llama_index.core.query_engine import NLSQLTableQueryEngine, RetrieverQueryEngine
from flask import g, current_app
from llama_index.core import SQLDatabase, ServiceContext
from llama_index.llms.gemini import Gemini
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from sqlalchemy import MetaData,create_engine
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core import Settings
from llama_index.embeddings.gemini import GeminiEmbedding
import os

def QueryLLM(query, db_url):
    engine = create_engine(db_url)
    Settings.llm = Gemini(model_name='models/gemini-pro', api_key=os.getenv('GOOGLE_API_KEY'))
    model_name = "models/embedding-001"

    Settings.embed_model = GeminiEmbedding(
        model_name=model_name, api_key=os.getenv('GOOGLE_API_KEY'), title="this is a document"
    )
    sql_database = SQLDatabase(engine)
    
    nl_sql_retriever = NLSQLRetriever(
        sql_database=sql_database,
        tables=["users"],
        return_raw=False
    )
    
    query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever)
    
    response = query_engine.query(query)
    
    print(str(response))
    return response