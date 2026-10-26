import json
from app.core.config import nebius_client, MODEL_NAME
from app.tools.db_tools import get_db_connection
from app.tools.rag_tools import search_internal_docs

def run_pipeline_agent(user_prompt: str) -> str:
    """
    An agent that debugs data pipelines using Airflow/DAG telemetry and 
    internal runbooks retrieved via RAG.
    """
    # 1. RAG Retrieval for pipeline SLAs, troubleshooting, and error policies
    retrieved_docs = search_internal_docs(user_prompt)
    rag_context = "\n\n".join([f"Source: {doc['title']}\nContent: {doc['content']}" for doc in retrieved_docs])
    if not rag_context:
        rag_context = "No specific internal documentation found for this pipeline query."

    # 2. Fetch recent pipeline run statuses from DuckDB telemetry table
    conn = get_db_connection()
    recent_runs = conn.execute("SELECT * FROM pipeline_runs ORDER BY run_date DESC;").fetchdf().to_dict(orient="records")
    conn.close()
    
    system_prompt = f"""
    You are an expert DataOps and Pipeline Engineering Agent. Your specialty is monitoring Apache Airflow 
    DAGs, analyzing pipeline failures, and identifying root causes.
    
    --- INTERNAL DOCUMENTATION (RAG) ---
    {rag_context}
    ------------------------------------
    
    --- TELEMETRY DATA ---
    {json.dumps(recent_runs, indent=2)}
    ----------------------
    
    Analyze the user's request using both the internal documentation policies and the live telemetry runs. 
    Explain why a pipeline failed or give actionable recommendations for fixing execution bottlenecks.
    """
    
    try:
        response = nebius_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error running Pipeline Agent: {str(e)}"