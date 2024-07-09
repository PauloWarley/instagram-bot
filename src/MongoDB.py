from pymongo import MongoClient


class MongoDB():
    def __init__(self):
       pass
   
    # Função para conectar ao MongoDB
    def connect_to_mongodb(self, uri):
        client = MongoClient(uri)
        return client

    # Função para buscar documento pelo user_name
    def find_document_by_username(self, db, collection_name, username):
        collection = db[collection_name]
        query = {"social_media.instagram.credentials.user_name": username}
        document = collection.find_one(query)
        return document

    def find_all_documents(self, db, collection_name):
        collection = db[collection_name]
        document = collection.find({})
        return document
    
    # Função para atualizar um documento
    def update_document(self, db, collection_name, query, update):
        collection = db[collection_name]
        result = collection.update_one(query, {"$set": update})
        return result

