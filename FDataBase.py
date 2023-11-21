import sqlite3
import math
import time
from flask import url_for
 
class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
 
    def getMenu(self):
        sql = '''SELECT * FROM review'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []
     
    def addReview(self, title, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO review VALUES(NULL, ?, ?, ?)", (title, text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД "+str(e))
            return False
 
        return True
    
    def getPost(self, alias):
        try:
            self.__cur.execute("SELECT title, text FROM review WHERE url LIKE ? LIMIT 1", (alias,))
            res = self.__cur.fetchone()
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД "+str(e))
 
        return (False, False)
    
    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, time FROM review ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД "+str(e))
        return []
