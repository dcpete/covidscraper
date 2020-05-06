# dependency: module python-dotenv
# variables must be stored in .env file
# more information in: https://pypi.org/project/python-dotenv/
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")