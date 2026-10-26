from typing import List, Dict

# Sample local vector database / knowledge base for your DataOps Copilot
KNOWLEDGE_BASE = [
    {
        "id": "doc_01",
        "title": "Pipeline SLA and Retry Policy",
        "content": "All daily sync pipelines (customer_daily_sync) must finish within 180 seconds. If a dbt transform fails due to lock contention, the workflow automatically retries after a 15-minute backoff window."
    },
    {
        "id": "doc_02",
        "title": "Schema Nomenclature Standards",
        "content": "All production table names must use snake_case prefix with domain scope (e.g., pipeline_runs, customer_events, inventory_snapshot). Raw landing tables must use the prefix 'landing_'."
    },
    {
        "id": "doc_03",
        "title": "Database Optimization Guide",
        "content": "When querying large DuckDB analytical tables, always filter by run_date to leverage column zone maps and avoid full table scans."
    }
]

def search_internal_docs(query: str, top_k: int = 2) -> List[Dict[str, str]]:
    """
    Performs a keyword-based retrieval (lexical search) over internal technical documentation 
    to fetch relevant context for the agent.
    """
    query_terms = query.lower().split()
    scored_results = []
    
    for doc in KNOWLEDGE_BASE:
        score = 0
        text_blob = (doc["title"] + " " + doc["content"]).lower()
        for term in query_terms:
            if term in text_blob:
                score += 1
        if score > 0:
            scored_results.append((score, doc))
            
    # Sort by highest score match
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    # Return top_k documents formatted
    matches = [doc for score, doc in scored_results[:top_k]]
    return matches