# Text to SQL Query Engine

This project enables users to connect to any database, input queries in natural human language, and retrieve relevant data by converting these queries into SQL. 
The project implements two different approaches to achieve this: one using pre-defined retrievers and query engines, and another using a Query Pipeline (DAG).

## Features

- **Natural Language Querying:** Input queries in plain human language and retrieve relevant data from a connected database.
- **SQL Conversion:** Automatically convert natural language queries into SQL statements.
- **Multiple Approaches:** 
  - **Pre-defined Retrievers and Query Engines:** Quick and straightforward implementation using `LlamaIndex` components.
  - **Query Pipeline (DAG):** A more advanced and flexible approach, allowing for complex workflows and data processing steps.

## Tech Stack

- **[LlamaIndex](https://github.com/jerryjliu/llama_index):** Used for building the natural language processing (NLP) components and managing the retrievers and query engines.
- **[Flask](https://flask.palletsprojects.com/):** Lightweight web framework used to build the API endpoints and handle incoming requests.
- **[Gemini](https://gemini.com/):** Leveraged for handling complex data processing and managing the execution of the query pipeline (DAG).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/text-to-sql.git
   cd text-to-sql

2. Create and activate a virtual environment:
   ```bash
   python3.10 -m venv venv

3. Activate Virtual environment
   ```bash
   source venv/bin/activate

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

5. Start The Server
   ```bash
   python main.py

## Run the Request and Get the Response using Postman

### POST Request

**URL:** `http://localhost:5000/database/connect-and-query`

**Method:** `POST`

### Request Body

```json
{
    "connection_string": "postgresql://postgres:postgres@localhost:5432/texttosql",
    "query": "Tell all the emails in users table?"
}
{
    "data": "\"assistant: Nipun@gmail.com, Anurag@gmail.com, Abc@gmail.com, Xyz@gmail.com\"",
    "message": "Success"
}
