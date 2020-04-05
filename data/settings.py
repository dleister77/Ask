import os

from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DATABASE_USER")
db_name = os.getenv("DATABASE_NAME")
db_password = os.getenv("DATABASE_PASSWORD")
