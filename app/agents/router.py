import json
from app.core.config import nebius_client, MODEL_NAME
from app.agents.sql_agent import run_sql_agent
from app.agents.pipeline_agent import run_pipeline_agent
from app.agents.terraform_agent import run_terraform_agent

def route_user_request(user_prompt: str) -> str:
    """
    Supervisor router that classifies user intent and delegates to either 
    the SQL Agent, Pipeline Agent, or Terraform Agent.
    """
    
    router_system_prompt = """
    You are the Lead Data Engineering Supervisor Agent. Your job is to analyze the user's request 
    and route it to the correct specialized agent:
    
    1. Choose "sql" if the user is asking about writing queries, inspecting table schemas, row counts, or database metrics.
    2. Choose "pipeline" if the user is asking about pipeline failures, Airflow DAG runs, execution times, or workflow errors.
    3. Choose "terraform" if the user is asking about provisioning cloud infrastructure, writing Terraform scripts, setting up S3 buckets, Snowflake warehouses, BigQuery datasets, or IAM policies.
    
    You must respond in strict JSON format:
    {
        "destination": "sql" or "pipeline" or "terraform",
        "reasoning": "brief explanation"
    }
    """
    
    try:
        router_response = nebius_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": router_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        routing_data = json.loads(router_response.choices[0].message.content)
        destination = routing_data.get("destination")
        
        if destination == "pipeline":
            return run_pipeline_agent(user_prompt)
        elif destination == "terraform":
            return run_terraform_agent(user_prompt)
        else:
            return run_sql_agent(user_prompt)
            
    except Exception as e:
        return run_sql_agent(user_prompt)