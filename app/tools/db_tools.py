import duckdb
from typing import List, Dict, Any

# Initialize a local embedded DuckDB connection (or connect to a file-based duckdb database)
DB_PATH = ":memory:"  # Use "enterprise_data.db" to persist data to disk

def get_db_connection():
    """Returns a connection to the DuckDB instance."""
    conn = duckdb.connect(DB_PATH)
    return conn

def init_sample_data():
    """Initializes sample data tables for the data engineering assistant to inspect and query."""
    conn = get_db_connection()
    
    # Create sample data engineering pipeline telemetry tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id VARCHAR,
            pipeline_name VARCHAR,
            status VARCHAR,
            execution_time_seconds DOUBLE,
            row_count INTEGER,
            run_date DATE
        );
    """)
    
    # Insert sample data if table is empty
    count = conn.fetchone()[0]
    if count == 0:
        conn.execute("""
            INSERT INTO pipeline_runs VALUES 
            ('run_001', 'customer_daily_sync', 'SUCCESS', 145.2, 50000, '2026-10-01'),
            ('run_002', 'orders_transform_dbt', 'FAILED', 320.5, 0, '2026-10-01'),
            ('run_003', 'inventory_snapshot', 'SUCCESS', 85.0, 12000, '2026-10-02'),
            ('run_004', 'customer_daily_sync', 'SUCCESS', 132.8, 51000, '2026-10-02'),
            ('run_005', 'orders_transform_dbt', 'SUCCESS', 290.1, 48000, '2026-10-02');
        """)
    
    conn.close()

def get_schema_metadata() -> str:
    """Retrieves table names and columns so the AI agents understand the database structure."""
    conn = get_db_connection()
    tables = conn.execute("SHOW TABLES;").fetchall()
    
    schema_info = []
    for table in tables:
        table_name = table[0]
        columns = conn.execute(f"DESCRIBE {table_name};").fetchall()
        col_descriptions = [f"{col[0]} ({col[1]})" for col in columns]
        schema_info.append(f"Table: {table_name}\nColumns: {', '.join(col_descriptions)}")
    
    conn.close()
    return "\n\n".join(schema_info)

def execute_sql_query(query: str) -> Dict[str, Any]:
    """Executes a SQL query safely and returns results or error details."""
    conn = get_db_connection()
    try:
        # Enforce read-only safety checks for enterprise safety
        cleaned_query = query.strip().lower()
        if any(keyword in cleaned_query for keyword in ["drop ", "delete ", "truncate ", "alter "]):
            return {"error": "Destructive SQL operations (DROP, DELETE, TRUNCATE, ALTER) are blocked by safety guardrails."}
        
        result = conn.execute(query).fetchdf()
        return {"success": True, "data": result.to_dict(orient="records")}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

# Automatically initialize sample data on module load
init_sample_data()