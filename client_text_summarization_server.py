import requests
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, start_page, end_page):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(start_page, end_page + 1):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def summarize_text(chapter_text):
    url = "http://localhost:5001/api/summarize"
    headers = {'Content-Type': 'application/json'}
    data = {'text': chapter_text}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('summary')
    else:
        return f"Error: {response.status_code}, {response.text}"

# Define the path to your PDF and the range of pages for the chapter you want to summarize
pdf_path = 'MATH_76_Paper.pdf'
start_page = 0  # Adjust as needed
end_page = 1    # Adjust as needed

# Extract text from the specified chapter
chapter_text = extract_text_from_pdf(pdf_path, start_page, end_page)

# Summarize the extracted text
summary = summarize_text(chapter_text)

# Print the summary
print("Summary:", summary)
