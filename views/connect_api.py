from flask_restx import Namespace, Resource
from flask import request, g, jsonify, current_app, make_response
from responses import BaseResponse
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from helpers.QueryPipeline import QueryLLM
import json
import pickle

connect_api = Namespace('database', 'This is used to connect database and execute queries')

@connect_api.route('/connect-and-query')
class ConnectAndQuery(Resource):
    def post(self):
        """
        Connect to the database and execute a query
        """
        data = request.get_json()

        if not data or 'connection_string' not in data or 'query' not in data:
            return BaseResponse.bad_request(400,'Both connection string and query are required')
        
        connection_string = data['connection_string']
        query = data['query']
        
        engine = create_engine(connection_string)
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * from users"))
            if not result.fetchone():
                raise SQLAlchemyError("Test query failed, cannot establish connection")
        
        # Execute the query using QueryLLM
        result = QueryLLM(query,db_url=connection_string)

        result_text = str(result)
                
        serialized_string = json.dumps(result_text)
        
        print(serialized_string)
        return BaseResponse.success(serialized_string)