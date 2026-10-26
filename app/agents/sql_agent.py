import json
from app.core.config import nebius_client, MODEL_NAME
from app.tools.db_tools import get_schema_metadata, execute_sql_query
from app.tools.rag_tools import search_internal_docs

def run_sql_agent(user_prompt: str) -> str:
    """
    An autonomous agentic workflow combining RAG (internal documentation search), 
    database schema introspection, and self-correcting SQL execution via Nebius.
    """
    
    # 1. RAG Retrieval: Fetch relevant internal docs/runbooks based on the prompt
    retrieved_docs = search_internal_docs(user_prompt)
    rag_context = "\n\n".join([f"Source: {doc['title']}\nContent: {doc['content']}" for doc in retrieved_docs])
    if not rag_context:
        rag_context = "No specific internal documentation found for this query."

    # 2. Fetch live database schema
    schema_context = get_schema_metadata()
    
    system_prompt = f"""
    You are an autonomous Enterprise Data Engineering Agent. Your goal is to solve the user's request 
    by leveraging internal documentation (RAG) and executing SQL queries against a DuckDB database.
    
    --- INTERNAL DOCUMENTATION (RAG) ---
    {rag_context}
    ------------------------------------
    
    --- DATABASE SCHEMA ---
    {schema_context}
    -----------------------
    
    You operate in a loop of Thought, Action, and Observation. 
    Respond in strict JSON format:
    {{
        "thought": "Your reasoning about what to check using the docs or SQL query",
        "sql_query": "The SQL query to run, or null if you have enough information from the docs or previous steps",
        "final_answer": "Your final detailed response to the data engineer"
    }}
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    max_iterations = 3
    current_iteration = 0
    
    while current_iteration < max_iterations:
        current_iteration += 1
        
        try:
            response = nebius_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            ai_message_content = response.choices[0].message.content
            parsed = json.loads(ai_message_content)
            
            sql_query = parsed.get("sql_query")
            final_answer = parsed.get("final_answer")
            
            # If the model gives a final answer without needing further queries, return it
            if final_answer and (not sql_query or sql_query.lower() == "null"):
                return final_answer
                
            # If a SQL query is requested, execute it in DuckDB
            if sql_query and sql_query.lower() != "null":
                execution_result = execute_sql_query(sql_query)
                
                # Append assistant thoughts and tool observation back to conversation history
                messages.append({"role": "assistant", "content": ai_message_content})
                
                if execution_result.get("success"):
                    obs_content = f"Observation: SQL executed successfully. Data results: {json.dumps(execution_result.get('data'))}"
                else:
                    obs_content = f"Observation: SQL execution failed with error: {execution_result.get('error')}. Please rewrite the query and try again."
                
                messages.append({"role": "user", "content": obs_content})
            else:
                return final_answer or ai_message_content
                
        except Exception as e:
            return f"Error in Agentic RAG Loop: {str(e)}"
            
    return "Agent reached maximum iterations without concluding."