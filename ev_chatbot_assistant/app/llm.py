import os
import yaml
from openai import OpenAI
from sqlalchemy import text
from app.db import engine
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client using the environment's API key
client = OpenAI()  # Automatically uses OPENAI_API_KEY
print("✅ OpenAI Client initialized successfully.")

# Load schema glossary from YAML file
with open("config/mapping.yaml") as f:
    MAPPING = yaml.safe_load(f)

# Helper: Build prompt with glossary and fleet constraint
def build_prompt(user_query: str, fleet_id: str) -> str:
    glossary = "\n".join([f"{k} → {v}" for k, v in MAPPING.items()])
    return f"""
You are a SQL assistant for an electric vehicle telemetry database.
Translate the following natural language question into a valid PostgreSQL query.
Make sure the query only returns data for: WHERE fleet_id = '{fleet_id}'.
Return SQL only — no explanation or markdown.

Glossary:
{glossary}

Question:
{user_query}
"""

# Main: Process the user's query through LLM, validate and run SQL
async def process_query(query: str, fleet_id: str):
    prompt = build_prompt(query, fleet_id)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    # Strip markdown formatting if exists
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").replace("```", "").strip()
    elif sql.startswith("```"):
        sql = sql.replace("```", "").strip()

    # Validate for dangerous operations
    if any(cmd in sql.lower() for cmd in ["delete", "drop", "update", "insert"]):
        raise ValueError("Unsafe SQL command detected.")

    # Add a limit if not already in query
    if "limit" not in sql.lower() and "count(" not in sql.lower():
        sql = sql.rstrip(";")
        sql += " LIMIT 5000"

    final_sql = sql
    print("\U0001F4DD SQL to execute:", final_sql)

    # Execute the query
    with engine.connect() as conn:
        result = conn.execution_options(timeout=10).execute(text(final_sql))
        rows = [dict(row._mapping) for row in result]

    # Format the result
    if not rows:
        return "No matching records found."
    elif len(rows[0]) == 1:
        return str(list(rows[0].values())[0])
    else:
        return rows

