import requests

# Function to extract text from PDF using the text extraction server
def extract_text_from_pdf(file_path, start_page, end_page):
    url = "http://localhost:5001/extract_text"
    files = {'file': open(file_path, 'rb')}
    data = {'start_page': start_page, 'end_page': end_page}
    response = requests.post(url, files=files, data=data)
    return response.json()['text']

# Function to summarize text using the Llama3 API
def llama3(prompt):
    url = "http://localhost:11434/api/chat"  # Ensure this is the correct URL for your local Llama3 instance
    data = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()['message']['content']

# Main function to extract text and generate summary
def main():
    file_path = "looma_sample_book.pdf"  # Replace with the path to your PDF
    start_page = 5
    end_page = 14
    
    chapter_1_text = extract_text_from_pdf(file_path, start_page, end_page)
    chapter_1_summary = llama3(f"Summarize the following text: {chapter_1_text}")
    
    print(f"Summary of Chapter 1:\n{chapter_1_summary}")
    
    with open("chapter_1_summary.txt", "w") as file:
        file.write(chapter_1_summary)
    
    print("Summary saved to chapter_1_summary.txt")

if __name__ == '__main__':
    main()
