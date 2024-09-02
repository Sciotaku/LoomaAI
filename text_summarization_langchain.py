from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.base import LLM  # Import the base LLM class
from pydantic import Field  # Import Field from pydantic
from pymongo import MongoClient
import fitz  # PyMuPDF
import io
import re
import requests
from typing import Optional, List
import pytesseract
from pdf2image import convert_from_bytes
import json

# Custom LLaMA3 Wrapper
class OllamaLlama3(LLM):
    api_url: str = Field(...)  # Declare api_url as a pydantic field

    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url

    @property
    def _llm_type(self) -> str:
        return "ollama_llama3"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = requests.post(
            self.api_url,
            json={"model": "llama3", "messages": [{"role": "user", "content": prompt}]},
            headers={"Content-Type": "application/json"},
            stream=True,  # Enable streaming response
        )
        response.raise_for_status()

        # Process the streaming response
        complete_message = []
        for line in response.iter_lines():
            if line:
                try:
                    json_line = json.loads(line.decode('utf-8'))  # Decode each line to a string
                    message_content = json_line.get("message", {}).get("content", "")
                    if message_content:
                        complete_message.append(message_content)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON response: {e}")
                    continue

        # Join all the parts together to form the complete message
        return ''.join(complete_message)

    def call(self, prompt: str) -> str:
        return self._call(prompt)


# Initialize MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")

# Initialize the LLaMA3 model using the Ollama API
llm = OllamaLlama3(api_url="http://localhost:11434/api/chat")

# Step 1: Text Extraction Function
def extract_text_from_pdf(url, first_page, last_page):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to download PDF from {url}. Status code: {resp.status_code}")
    
    pdf = io.BytesIO(resp.content)
    text = ""
    with fitz.open(stream=pdf, filetype="pdf") as doc:
        for page_num in range(first_page, last_page):
            page = doc.load_page(page_num)
            extracted_text = page.get_text()
            if extracted_text.strip():
                text += extracted_text
            else:
                images = convert_from_bytes(resp.content, first_page=page_num+1, last_page=page_num+1)
                for image in images:
                    text += pytesseract.image_to_string(image)
    return text

# Step 2: Define the summarization prompt
prompt_template = """Summarize the following text:

{text}

Summarize it in a concise manner, focusing on the key points.
"""

prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

# Step 3: Define the LLM chain using LangChain
summarization_chain = LLMChain(llm=llm, prompt=prompt)

# Step 4: Function to summarize a chapter using its ID
def summarize_chapter(chapter_id):
    # Query MongoDB for the chapter
    chapter = db.chapters.find_one({"_id": chapter_id})
    if not chapter:
        raise Exception(f"Chapter with ID {chapter_id} not found.")
    
    groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\\.[0-9]{2})?",
                       chapter['_id'], re.IGNORECASE)
    grade_level = groups[1]  # grade level
    subject = groups[2]
    first_page = chapter['pn']
    last_page = chapter['pn'] + chapter['len']
    if first_page == "" or last_page == "":
        raise Exception("Invalid page numbers")
    
    # Retrieving the corresponding textbook
    textbook = db.textbooks.find_one({"prefix": grade_level + subject})
    if not textbook:
        raise Exception(f"Textbook with prefix {grade_level + subject} not found.")
    
    # Constructing the URL to download the PDF
    url = f"https://looma.website/content/{textbook['fp']}{textbook['fn']}"
    
    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(url, first_page, last_page)
    
    # Split text if it's too long for the LLM
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50
    )
    text_chunks = text_splitter.split_text(extracted_text)

    # Summarize each chunk and combine summaries
    summaries = [summarization_chain.invoke({"text": chunk}) for chunk in text_chunks]
    return "\n".join(summaries)

# Example usage
if __name__ == "__main__":
    chapter_id = input("Enter the chapter ID (e.g., 10S01): ")
    try:
        summary = summarize_chapter(chapter_id)
        print("Summary:")
        print(summary)
    except Exception as e:
        print(f"Error: {e}")