import sqlite3

class BlogDataBase:
    def __init__(self, db):
        self.db = db
        self.cur = db.cursor()
    
    def convert_to_binary_img(self, img):
        with open(img, 'rb') as file:
            blob_data = file.read()
        return blob_data
    
    def insert_blob(self, id, title, content, img, img_name):
        try:
            insert_blob_query = """REPLACE INTO posts
                                    (id, title, content, img, img_name) VALUES (?, ?, ?, ?, ?)"""
            converted_img = self.convert_to_binary_img(img)
            data_tuple = (id, title, content, converted_img, img_name)
            self.cur.execute(insert_blob_query, data_tuple)
            self.db.commit()
            # self.cur.close()
        except sqlite3.Error as error:
            print("!Ошибка при работе с SQLite", error)
