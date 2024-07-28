from pymongo import MongoClient
import gridfs
import os

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")
fs = gridfs.GridFS(db)

def download_pdf(chapter_id):
    # Fetch the chapter for the given chapter ID
    chapter = db.chapters.find_one({"_id": chapter_id})
    if not chapter:
        print(f"Chapter with ID {chapter_id} not found.")
        return
    
    textbook_prefix = chapter_id[:-2]  # Extract the prefix from the chapter ID
    textbook = db.textbooks.find_one({"prefix": textbook_prefix})
    if not textbook:
        print(f"Textbook for chapter ID {chapter_id} not found.")
        return
    
    # Get the filename and path
    pdf_filename = textbook["fn"]
    pdf_filepath = textbook["fp"]

    # Assume that PDFs are stored in GridFS
    # Fetch the file from GridFS
    file_data = fs.find_one({"filename": os.path.join(pdf_filepath, pdf_filename)})
    if not file_data:
        print(f"PDF file {pdf_filename} not found in GridFS.")
        return

    # Save the file locally
    output_file_path = os.path.join("/desired/path/to/save", pdf_filename)
    with open(output_file_path, 'wb') as output_file:
        output_file.write(file_data.read())
    
    print(f"PDF file {pdf_filename} has been downloaded to {output_file_path}.")

if __name__ == "__main__":
    chapter_id = "10S01"  # You can change this ID to any other chapter ID
    download_pdf(chapter_id)