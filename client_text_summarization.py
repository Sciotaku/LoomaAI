import requests
import json

# Function to extract text from PDF using the text extraction server
def extract_text_from_pdf(file_path, start_page, end_page):
    url = "http://localhost:5001/extract_text"
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {'start_page': start_page, 'end_page': end_page}
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()['text']
    except requests.exceptions.RequestException as e:
        print(f"Error during text extraction: {e}")
        return None

# Function to summarize text using the Llama3 API
def llama3(prompt):
    url = "http://localhost:11434/api/chat"  
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
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error during summarization: {e}")
        return None

# Main function to extract text and generate summary
def main():
    file_path = "looma_sample_book.pdf" 
    start_page = 5
    end_page = 14
    
    chapter_1_text = extract_text_from_pdf(file_path, start_page, end_page)
    if chapter_1_text:
        chapter_1_summary = llama3(f"Summarize the following text: {chapter_1_text}")
        
        if chapter_1_summary:
            print(f"Summary of Chapter 1:\n{chapter_1_summary}")
            
            with open("chapter_1_summary.txt", "w") as file:
                file.write(chapter_1_summary)
            
            print("Summary saved to chapter_1_summary.txt")
        else:
            print("Failed to generate summary.")
    else:
        print("Failed to extract text from PDF.")

if __name__ == '__main__':
    main()