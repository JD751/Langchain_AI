

from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv
load_dotenv()

api_key= os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI()

llm = ChatOpenAI(openai_api_key=api_key)

print(llm.invoke("What is the biggest beach in Poland?"))