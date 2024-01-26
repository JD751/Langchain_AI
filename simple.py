# %%
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the language model
llm = ChatOpenAI(openai_api_key=api_key, max_tokens=100, temperature=0.7)

# %%
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a language model that can extract information from texts."),
    ("user", "{input}")
])

chain = prompt | llm


# %%
from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()
chain = chain | output_parser


# %%
import pdfplumber

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Extract text from the PDF
pdf_text = extract_text_from_pdf("menu.pdf")

# Invoke the chain with your query
response = chain.invoke({"input": "write a quote about pizza from the following text" + pdf_text})

# Print the response
print(response)
#print(pdf_text)

# %%



