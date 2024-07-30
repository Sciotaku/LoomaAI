from pymongo import MongoClient
import fitz  # PyMuPDF
import io
import requests
from pdf2image import convert_from_bytes
import pytesseract
import nltk
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from nltk.corpus import stopwords

# Download NLTK data
nltk.download('stopwords')
nltk.download('punkt')

# MongoDB client setup
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")
 
# Initialize stop words
stop_words = set(stopwords.words('english'))

def extract_text_from_page(page):
    text = page.get_text()
    if text.strip():  # If text is found, return it
        return text
    else:  # Otherwise, use OCR
        return None

def perform_ocr(image):
    return pytesseract.image_to_string(image)

def preprocess_text(text):
    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    # Remove stop words and non-alphabetic tokens
    tokens = [token.lower() for token in tokens if token.isalpha() and token.lower() not in stop_words]
    return tokens

def extract_text_from_pdf(url, first_page, last_page):
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to download PDF from {url}. Status code: {resp.status_code}")
        return ""
    
    pdf = io.BytesIO(resp.content)
    text = ""
    with fitz.open(stream=pdf, filetype="pdf") as doc:
        for page_num in range(first_page, last_page):
            page = doc.load_page(page_num)
            extracted_text = extract_text_from_page(page)
            if extracted_text:
                text += extracted_text
            else:
                images = convert_from_bytes(resp.content, first_page=page_num+1, last_page=page_num+1)
                for image in images:
                    text += perform_ocr(image)
    return text

def generate_topics(chapter_texts, num_topics=5, num_words=5):
    # Preprocess texts
    processed_texts = [preprocess_text(text) for text in chapter_texts]
    # Create a dictionary and corpus
    dictionary = corpora.Dictionary(processed_texts)
    corpus = [dictionary.doc2bow(text) for text in processed_texts]
    # Train LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    # Extract topics
    topics = lda_model.print_topics(num_words=num_words)
    return topics

def generate_chapter_topics(chapter_id):
    # Access the chapters collection
    chapters_collection = db.get_collection("chapters")
    textbooks_collection = db.get_collection("textbooks")
    
    chapter = chapters_collection.find_one({"_id": chapter_id})
    if not chapter:
        print(f"Chapter with ID {chapter_id} not found.")
        return
    
    try:
        grade_level = chapter_id[:-2]
        textbook = textbooks_collection.find_one({"prefix": grade_level})
        if not textbook:
            print(f"Textbook for prefix {grade_level} not found.")
            return
        
        first_page = chapter['pn']
        last_page = chapter['pn'] + chapter['len']
        url = f"https://looma.website/content/{textbook['fp']}{textbook['fn']}"
        chapter_text = extract_text_from_pdf(url, first_page, last_page)
        
        topics = generate_topics([chapter_text])
        print(f"Topics for Chapter {chapter_id}: {topics}")
        
    except Exception as e:
        print(f"Error processing chapter {chapter['_id']}: {e}")

if __name__ == "__main__":
    chapter_id = input("Enter the chapter ID (e.g., 10S01): ")
    generate_chapter_topics(chapter_id)