import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, start_page, end_page):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(start_page, end_page + 1):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

pdf_path = 'MATH_76_Paper.pdf'
start_page = 0  # start of chapter
end_page = 1    # end of chapter
chapter_text = extract_text_from_pdf(pdf_path, start_page, end_page)
print(chapter_text)
