import os
from dotenv import load_dotenv

load_dotenv()
print("🔑 OPENAI KEY:", os.getenv("OPENAI_API_KEY"))

