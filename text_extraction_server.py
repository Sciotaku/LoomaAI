from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import os

app = Flask(__name__)

# Define a function to extract text from a page using PyMuPDF
def extract_text_from_page(page):
    text = page.get_text()
    if text.strip():  # If text is found, return it
        return text
    else:  # Otherwise, use OCR
        return None

# Define a function to perform OCR on an image of a page
def perform_ocr(image):
    return pytesseract.image_to_string(image)

# Define a function to extract text from a PDF, handling both text and scanned pages
def extract_text_from_pdf(pdf_path, start_page, end_page):
    pdf_document = fitz.open(pdf_path)
    text_by_page = []

    for page_num in range(start_page - 1, end_page):
        page = pdf_document.load_page(page_num)
        text = extract_text_from_page(page)
        if text is None:
            # If no text is found, convert the page to an image and perform OCR
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
            text = perform_ocr(images[0])
        text_by_page.append(text)
    return text_by_page

@app.route('/extract_text', methods=['POST'])
def extract_text():
    file = request.files['file']
    start_page = int(request.form.get('start_page', 1))
    end_page = int(request.form.get('end_page', 1))

    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)
    
    text_by_page = extract_text_from_pdf(file_path, start_page, end_page)
    os.remove(file_path)
    
    return jsonify({"text": "\n".join(text_by_page)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
