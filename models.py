"""
Описує моделі для наповнення БД hw_09. Безпосередньо передача даних до БД
з файлів authors.json та quotes.json відбувається в create.py.
"""


from mongoengine import *


uri = "mongodb+srv://goitlearn:goit_web_db_mongodb@cluster0.sgtae2n.mongodb.net/hw_09?retryWrites=true&w=majority"
# обов'язково вказати 'host='
connect(host=uri, ssl=True)


# Описуємо колекцію Author
class Author(Document):
    fullname = StringField(max_length=50)
    born_date = StringField(max_length=50)
    born_location = StringField(max_length=150)
    description = (
        StringField()
    )  # цитати занадто довгі, тому не ставимо ліміт на кількість символів в рядку


# Описуємо колекцію Quote
class Quote(Document):
    # список полів
    tags = ListField(max_length=50)
    # ReferenceField - аналог ForeignKey, зберігає object_id з іншого документа
    # У випадку необхідності знищення постів при видаленні User: reverse_delete_rule=CASCADE
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    quote = StringField()
    # Для подальшого розширення моделей через наслідування від Quote
    # (див. https://docs.mongoengine.org/tutorial.html) записуємо:
    meta = {"allow_inheritance": True}
