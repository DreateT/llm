from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/datakrew_db")
engine = create_engine(DATABASE_URL)

