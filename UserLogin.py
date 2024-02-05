class UserLogin:
    def fromDB(self, user_id, db): # будет использоваться при создании объекта в декораторе user_loader (когда будет приходить запрос от браузера)
        self.__user = db.getUser(user_id)
        return self 
 
    def create(self, user): # вызывается, когда пользователь проходит авторизацию на сайте
        self.__user = user
        return self
 
    def is_authenticated(self): # проверка авторизации пользователя (для упрощения программы (см. далее) - true)
        return True
 
    def is_active(self): # проверка, активен ли пользователь
        return True
 
    def is_anonymous(self): # проверка неавторизованных пользователей
        return False
 
    def get_id(self): # возвращает айди пользователя
        return str(self.__user['id'])
    
    # в __user хранится вся информация, находящаяся в БД
    def getName(self):
        return self.__user['name'] if self.__user else "Без имени"
 
    def getEmail(self): 
        return self.__user['email'] if self.__user else "Без email"
    
    def getAvatar(self, app):
      '''Получение аватара'''
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f: 
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: "+str(e))
        else:
            img = self.__user['avatar']
        return img
    
    def verifyExt(self, filename):
        '''Проверяет расширение загружаемого на аватар файла'''
        ext = filename.rsplit('.', 1)[1] # разделение файла с конца
        if ext == "png" or ext == "PNG":
            return True
        return False
