import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
YOUR_TABLE_NAME = os.getenv("TABLE_NAME", "")
OBJECTIVE = os.getenv("OBJECTIVE", "")
DO_RETRY = bool(os.getenv("DO_RETRY", 1))
PLANNER_AGENT_OUTPUT_STRING = "Planner Agent Output: "
WORKING_DIRECTORY = os.getenv('WORKING_DIRECTORY', '/path/to/working/directory')

WORKING_DIRECTORY = os.getenv("WORKING_DIRECTORY", "/path/to/working/directory")
