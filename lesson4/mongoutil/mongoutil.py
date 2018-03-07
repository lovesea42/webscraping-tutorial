from pymongo import MongoClient

class BookDataMongoUtil:

    def __init__(self,host,port):
        self.conn = MongoClient(host, port)
        self.db = self.conn.book

    def add_book_data(self,data):
        self.db.col.insert(data)
