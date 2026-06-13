from dotenv import load_dotenv
import os
load_dotenv(verbose=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALIBAILIAN_API_KEY=os.getenv("ALIBAILIAN_API_KEY")
ALIBAILIAN_BASE_URL=os.getenv("ALIBAILIAN_BASE_URL")
MiniMax_API_KEY = os.getenv("MiniMax_API_KEY")
MiniMax_BASE_URL = os.getenv("MiniMax_BASE_URL")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_BASE_URL = os.getenv("ZHIPU_BASE_URL")