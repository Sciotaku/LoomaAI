from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.get_database("looma")

# List all textbooks and chapters
def list_ids():
    textbooks = db.get_collection("textbooks")
    chapters = db.get_collection("chapters")

    print("Textbook Prefixes:")
    for textbook in textbooks.find({}, {"prefix": 1}):
        print(textbook["prefix"])

    print("\nChapter IDs:")
    for chapter in chapters.find({}, {"_id": 1}):
        print(chapter["_id"])

if __name__ == "__main__":
    list_ids()