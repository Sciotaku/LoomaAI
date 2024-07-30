from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")

def generate_chapter_ids():
    # Access the chapters collection
    chapters_collection = db.get_collection("chapters")
    
    # Fetch all chapter IDs
    chapter_ids = chapters_collection.find({}, {"_id": 1})
    
    # Generate a list of chapter IDs
    chapter_id_list = [chapter["_id"] for chapter in chapter_ids]
    
    return chapter_id_list

if __name__ == "__main__":
    chapter_ids = generate_chapter_ids()
    print("List of Chapter IDs:")
    for chapter_id in chapter_ids:
        print(chapter_id)