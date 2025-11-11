import os
from dotenv import load_dotenv

load_dotenv()

# Get absolute path to the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '../database/qslrm.db')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
