import os
#import openai
import yaml

from openai import OpenAI
from sqlalchemy import text
from app.db import engine
from dotenv import load_dotenv

# Load my OpenAI API key (use .env or secure config in real app)
load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")


# Initialize OpenAI client
client = OpenAI()  #  reads the API key automatically from the environment
print("Client initialized successfully.")

# Load schema mappings file ... (glossary)
with open("config/mapping.yaml") as f:
    MAPPING = yaml.safe_load(f)


# Step 1: Build LLM prompt
def build_prompt(user_query: str, fleet_id: str):
    glossary = "\n".join([f"{k} → {v}" for k, v in MAPPING.items()])
    return f"""
You are a SQL assistant for an electric vehicle telemetry database.
Translate the following question into a PostgreSQL SQL query.
Only access data for the user's fleet using: WHERE fleet_id = '{fleet_id}'
Return SQL only, no explanation.

Glossary:
{glossary}

Question:
{user_query}
"""

# Step 2: Call LLM, execute SQL, return result
async def process_query(query: str, fleet_id: str):
    prompt = build_prompt(query, fleet_id)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    # Check for unsafe commands
    if any(cmd in sql.lower() for cmd in ["delete", "drop", "update", "insert"]):
        raise ValueError("Unsafe SQL command detected.")


    # Limit rows and set timeout
    if "limit" not in sql.lower() and "count(" not in sql.lower():
        sql += " LIMIT 5000"
    final_sql = sql

	
    with engine.connect() as conn:
        result = conn.execution_options(timeout=10).execute(text(final_sql))    
        rows = [dict(row) for row in result]

    return {
        "query": sql,
        "rows": rows
    }

    # For production use
    if not rows:
        return "No matching records found."
    elif len(rows[0]) == 1:
        return str(list(rows[0].values())[0])  # single value
    else:
        return rows


