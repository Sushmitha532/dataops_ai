import json
from app.core.config import nebius_client, MODEL_NAME
from app.tools.rag_tools import search_internal_docs

def run_terraform_agent(user_prompt: str) -> str:
    """
    An agent that generates Terraform infrastructure code guided by internal 
    cloud architecture guidelines retrieved via RAG.
    """
    # 1. RAG Retrieval for enterprise infrastructure standards and security guidelines
    retrieved_docs = search_internal_docs(user_prompt)
    rag_context = "\n\n".join([f"Source: {doc['title']}\nContent: {doc['content']}" for doc in retrieved_docs])
    if not rag_context:
        rag_context = "No specific internal infrastructure guidelines found."

    system_prompt = f"""
    You are an expert Cloud Infrastructure and DevOps Engineer specializing in DataOps. 
    Your job is to write secure, production-ready Terraform (HCL) configurations for data engineering 
    infrastructure (AWS S3, Snowflake warehouses, BigQuery datasets, IAM roles).
    
    --- INTERNAL INFRASTRUCTURE STANDARDS (RAG) ---
    {rag_context}
    ------------------------------------------------
    
    When writing Terraform code:
    1. Align with the internal standards and naming conventions provided in the RAG context.
    2. Follow best practices (variables, encryption enabled, proper resource tagging).
    3. Output clean, valid HCL code blocks with deployment explanations.
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
        return f"Error running Terraform Agent: {str(e)}"